"""
Beer Recommender ML Model - Standalone version using data/ directory.
"""
import pandas as pd
import numpy as np
import os
import json
from groq import Groq
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import NearestNeighbors
from typing import Dict, List, Optional

# Get data directory path
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


class BeerRecommender:
    def __init__(self):
        self.df = None
        self.gb_model = None
        self.global_scaler_recommend = None
        self.scalar = None
        self.encoder = None
        self.encoder2 = None
        self.X_reg_scaled = None
        self.scaling_features = ['ABV', 'Astringency', 'Body', 'Alcohol', 'Bitter',
                                 'Sweet', 'Sour', 'Salty', 'Fruits', 'Hoppy', 'Spices', 'Malty']
        self.mainstream_patterns = [
            'co.', 'inc', 'budweiser', 'bud', 'busch', 'michelob',
            'miller', 'coors', 'keystone', 'blue moon',
            'pabst', 'pbr', 'schlitz', 'old milwaukee',
            'rolling rock', 'yuengling', 'natural light', 'natty',
            'samuel adams', 'sam adams', 'boston lager',
            'corona', 'modelo', 'pacifico',
            'dos equis', 'tecate', 'sol', 'victoria',
            'heineken', 'amstel', 'stella artois',
            'becks', "beck's", 'st pauli', 'warsteiner',
            'guinness', 'harp', 'smithwick', 'kilkenny',
            'peroni', 'moretti', 'nastro azzurro',
            'carlsberg', 'tuborg', 'kronenbourg',
            'fosters', "foster's", 'grolsch', 'pilsner urquell',
            'molson', 'labatt', 'moosehead', 'sleeman',
            'sapporo', 'asahi', 'kirin', 'tsingtao', 'singha', 'tiger', 'leo',
            'shock top', 'goose island', 'elysian', 'lagunitas',
            'ballast point', '10 barrel', 'golden road',
            'blue point', 'devils backbone', 'karbach',
            'breckenridge', 'four peaks', 'wicked weed',
            'sierra nevada', 'new belgium', 'fat tire',
            'stone', 'brooklyn', 'dogfish head', 
            "bell's", 'bells brewery', 'founders',
            'deschutes', 'rogue', 'anchor steam',
            'red stripe', 'newcastle', 'bass', 'boddingtons',
            'murphy', 'beamish', 'tennents', 'carling',
            'leinenkugel', 'magic hat', 'pyramid',
            'widmer', 'redhook', 'kona', 'longboard',
            'landshark', 'presidente', 'medalla',
            'kingfisher', 'haywards', 'thunderbolt',
            'kalyani', 'knockout', 'royal challenge',
            'carlsberg elephant', 'bira 91', 'bira',
            'simba', 'godfather', 'hunter', 'zingaro',
            'london pilsner', 'kotsberg', 'bullet',
            'khajuraho', 'taj mahal', 'flying horse', 'dansberg',
            'golden eagle', 'guru', 'bad monkey', 'bee young',
            'white rhino', 'white owl', 'effingut'
        ]
        
    def load_and_preprocess_data(self):
        """Load and preprocess beer data from CSV."""
        csv_path = os.path.join(_DATA_DIR, "beer_profile_and_ratings.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Beer data file not found: {csv_path}")
        
        self.df = pd.read_csv(csv_path)
        
        self.df['mainstream'] = self.df.apply(
            lambda row: self.matches_mainstream_pattern(row['Beer Name (Full)']), axis=1
        )
        self.df['mainstream'] = self.df['mainstream'] | (self.df['number_of_reviews'] >= 300)
        
        self.df['strength'] = self.df['ABV'].apply(
            lambda x: 'Light' if x <= 5 else
                      'Medium' if x <= 7 else
                      'Strong' if x <= 10 else
                      'Extra Strong'
        )
        
        self.df = self.df.drop(columns=['Min IBU', 'Max IBU', 'review_aroma', 
                                        'review_appearance', 'review_palate', 
                                        'review_taste', 'Beer Name (Full)', 'Brewery'], errors='ignore')
        
        cols = self.df.columns.tolist()
        if len(cols) > 2:
            cols[1], cols[2] = cols[2], cols[1]
            self.df = self.df[cols]
        self.df['mainstream'] = self.df['mainstream'].astype(int)
        
    def matches_mainstream_pattern(self, beer_name_full):
        """Check if beer name matches mainstream patterns."""
        if pd.isna(beer_name_full):
            return False
        combined_name = str(beer_name_full).lower()
        for pattern in self.mainstream_patterns:
            if pattern in combined_name:
                return True
        return False
    
    def train_regression_model(self):
        """Train the gradient boosting regression model."""
        reg_df = self.df.drop(columns=['number_of_reviews', 'strength', 'Name', 'Description'], errors='ignore')
        
        cols = reg_df.columns.tolist()
        if len(cols) > 2:
            cols[-2], cols[-1] = cols[-1], cols[-2]
            reg_df = reg_df[cols]
        
        y_reg = reg_df.iloc[:, -1]
        X_reg = reg_df.iloc[:, :-1]
        
        X = X_reg.copy()
        
        self.scalar = MinMaxScaler()
        X[self.scaling_features] = self.scalar.fit_transform(X[self.scaling_features])
        
        X['Style'] = X['Style'].str.split(' - ').str[0].str.split(' / ').str[0]
        
        self.encoder = OneHotEncoder(sparse_output=False)
        encoded_array = self.encoder.fit_transform(X[['Style']])
        feature_names = self.encoder.get_feature_names_out(['Style'])
        encoded_df = pd.DataFrame(encoded_array, columns=feature_names, index=X_reg.index)
        
        self.X_reg_scaled = pd.concat([X.drop('Style', axis=1), encoded_df], axis=1)
        
        X_train = self.X_reg_scaled.to_numpy()
        y_train = y_reg.to_numpy()
        
        self.gb_model = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=4
        )
        self.gb_model.fit(X_train, y_train)
        
        self.global_scaler_recommend = MinMaxScaler()
        self.global_scaler_recommend.fit(self.df[self.scaling_features])
        
    def get_beer_features_from_text(self, user_input: str) -> Dict:
        """Get beer features from text using Groq API."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found")
            
            client = Groq(api_key=api_key)
            
            system_prompt = """
            You are a beer flavor profile translator. Convert natural language beer preferences into numerical flavor profiles.

            Return a JSON with these exact fields:
            - ABV: (float) 0.0-57.5
            - Astringency: (int) 0-81
            - Body: (int) 0-175
            - Alcohol: (int) 0-139
            - Bitter: (int) 0-150
            - Sweet: (int) 0-263
            - Sour: (int) 0-284
            - Salty: (int) 0-48
            - Fruits: (int) 0-175
            - Hoppy: (int) 0-172
            - Spices: (int) 0-184
            - Malty: (int) 0-239
            - mainstream: (int) 0 or 1 (DEFAULT = 1)
            - style: (string) Beer style category

            DEFAULT mainstream = 1. Only set to 0 for Belgian styles, Sour/Wild, Imperial/Dessert beers with ABV > 9, or explicit "craft"/"artisanal" requests.
            """
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error calling GROQ API: {e}")
    
    def predict_rating(self, llm_output: Dict) -> float:
        """Predict beer rating from features."""
        test_point = {col: 0 for col in self.X_reg_scaled.columns}
        
        for feat in self.scaling_features:
            test_point[feat] = [llm_output[feat]]
        
        test_point['mainstream'] = llm_output['mainstream']
        
        style_column = f"Style_{llm_output['style']}"
        if style_column in self.X_reg_scaled.columns:
            test_point[style_column] = 1
        
        test_point = pd.DataFrame(test_point)
        test_point[self.scaling_features] = self.scalar.transform(test_point[self.scaling_features])
        test_point = test_point[self.X_reg_scaled.columns]
        
        test_point = test_point.to_numpy()
        predicted_rating = self.gb_model.predict(test_point.reshape(1, -1))[0]
        
        return predicted_rating
    
    def get_strength(self, ABV: float) -> str:
        """Get strength category from ABV."""
        if ABV <= 5:
            return 'Light'
        elif ABV <= 7:
            return 'Medium'
        elif ABV <= 10:
            return 'Strong'
        else:
            return 'Extra Strong'
    
    def get_quality_score(self, rating: float, num_reviews: int) -> float:
        """Calculate quality score from rating and review count."""
        return rating * (0.6 + 0.4 * np.log1p(num_reviews) / 10)
    
    def get_beer_recommendations(self, llm_output: Dict, alt: bool = False, alt_rating_threshold: float = 3.0) -> List[Dict]:
        """Get beer recommendations using KNN."""
        X_recommend = self.df[['Style'] + self.scaling_features + ['mainstream', 'strength']].copy()
        y_recommend = self.df[['Name', 'Description', 'review_overall', 'number_of_reviews']].copy()
        
        X_recommend['Style'] = X_recommend['Style'].str.split(' - ').str[0].str.split(' / ').str[0]
        
        self.encoder2 = OneHotEncoder(sparse_output=False)
        encoded_array = self.encoder2.fit_transform(X_recommend[['Style']])
        feature_names = self.encoder2.get_feature_names_out(['Style'])
        encoded_df = pd.DataFrame(encoded_array, columns=feature_names, index=X_recommend.index)
        X_recommend = pd.concat([X_recommend.drop('Style', axis=1), encoded_df], axis=1)
        
        if alt:
            rating_mask = y_recommend['review_overall'] >= alt_rating_threshold
            X_recommend = X_recommend[rating_mask]
            y_recommend = y_recommend[rating_mask]
        
        if llm_output['mainstream'] == 1:
            mainstream_mask = X_recommend['mainstream'] == 1
            X_recommend = X_recommend[mainstream_mask]
            y_recommend = y_recommend[mainstream_mask]
        
        strength = self.get_strength(llm_output['ABV'])
        strength_mask = X_recommend['strength'] == strength
        X_recommend_sub = X_recommend[strength_mask]
        y_recommend_sub = y_recommend[strength_mask]
        
        X_recommend_sub = X_recommend_sub.drop(columns=['strength', 'mainstream'])
        
        X_recommend_sub[self.scaling_features] = self.global_scaler_recommend.transform(
            X_recommend_sub[self.scaling_features]
        )
        
        X_recommend_scaled = X_recommend_sub
        X_recommend_scaled_np = X_recommend_scaled.to_numpy()
        y_recommend_np = y_recommend_sub.to_numpy()
        
        # Generate test point
        test_point = {col: 0 for col in X_recommend_scaled.columns}
        for feat in self.scaling_features:
            test_point[feat] = [llm_output[feat]]
        
        style_column = f"Style_{llm_output['style']}"
        if style_column in X_recommend_scaled.columns:
            test_point[style_column] = 1
        
        test_point = pd.DataFrame(test_point)
        test_point[self.scaling_features] = self.global_scaler_recommend.transform(
            test_point[self.scaling_features]
        )
        test_point = test_point[X_recommend_scaled.columns]
        test_point_np = test_point.values[0]
        
        knn = NearestNeighbors(n_neighbors=10, metric='euclidean')
        knn.fit(X_recommend_scaled_np)
        
        distances, indices = knn.kneighbors([test_point_np])
        
        top_10_beers = []
        for i, idx in enumerate(indices[0]):
            beer_info = {
                'name': y_recommend_np[idx][0],
                'description': y_recommend_np[idx][1],
                'rating': y_recommend_np[idx][2],
                'num_reviews': y_recommend_np[idx][3],
                'distance': distances[0][i],
                'index': idx
            }
            top_10_beers.append(beer_info)
        
        for beer in top_10_beers:
            beer['quality_score'] = self.get_quality_score(beer['rating'], beer['num_reviews'])
        
        top_10_beers.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return top_10_beers[:2]
    
    def get_recommendations(self, user_input: str) -> Dict:
        """Get beer recommendations from user input."""
        llm_output = self.get_beer_features_from_text(user_input)
        predicted_rating = self.predict_rating(llm_output)
        
        # Get regular recommendations
        recommendations = self.get_beer_recommendations(llm_output, alt=False)
        
        # Get alternative recommendations if rating is low
        alt_recommendations = None
        if predicted_rating < 3.0:
            alt_recommendations = self.get_beer_recommendations(llm_output, alt=True, alt_rating_threshold=3.0)
        
        return {
            'predicted_rating': predicted_rating,
            'recommendations': recommendations,
            'alt_recommendations': alt_recommendations,
            'user_features': llm_output
        }
