# Dependencies
import joblib as jbl
import redis
import pandas as pd
import json


# Deserializing the data and passing it as a list of value (dataframes) and key (file name) pairs
imdb250_data = jbl.load('data/zipped_data.joblib')
imdb250_data_items = list(imdb250_data)  


# Establishing Redis connection (instance from Render)
redis_url = os.getenv('REDIS_URL')
r = redis.Redis.from_url(redis_url)


# Creating a class to retrieve data for deployment
class Imdb250Data:
    
    # A global method for computing cached data
    def compute_cached_data(self, data_items: list[tuple[pd.DataFrame, str]]) -> pd.DataFrame:        
        value, key = data_items        
        json_data = value.to_json()            
        r.set(key, json_data)
        cached_data = pd.DataFrame(json.loads(json_data))          
        return cached_data
    
    # Global method for getting cached data (or recompute in case it is no longer available)
    def get_cached_data(self, data_items: list[tuple[pd.DataFrame, str]]) -> pd.DataFrame:        
        value, key = data_items
        cached_data = r.get(key)
        if cached_data:
                return pd.DataFrame(json.loads(cached_data))
        else:
                return self.compute_cached_data(data_items)

    # Method for fetching the IMDb 250 in a dataframe
    def imdb250_data(self) -> pd.DataFrame:
        return self.get_cached_data(imdb250_data_items[0])
        
    # Method for getting dataframe with similarity scores
    def imdb250_similarities(self) -> pd.DataFrame:
        return self.get_cached_data(imdb250_data_items[1])
                       
    # Method for getting recommendations based on user preference
    def get_recommendations(self, user_preferences: list[str]) -> list[str]:
        similarities_df = self.imdb250_similarities()
        preferences_series = pd.concat(
             [similarities_df[preference] for preference in user_preferences]
                                       ).sort_values(ascending = False)
        not_in_preferences_series = preferences_series[~(preferences_series.index.isin(user_preferences))]
        not_duplicated_series = not_in_preferences_series[~(not_in_preferences_series.index.duplicated())] 
        filtered_df = not_duplicated_series.to_frame('score')
        top_recommendations = filtered_df.query('score  >= .55')
        if len(top_recommendations) >= 5:
            return list(top_recommendations.index[:5])
        else:
            return list(not_duplicated_series.index[:5])