# Dependencies
import joblib as jbl
import redis
import pandas as pd
import json
from urllib.parse import urlparse



# Deserializing the data and passing it as list of value (dataframes) and key (file name)
imdb250_data_zipped_file = 'imdb250_data_zipped.joblib'
imdb250_data = jbl.load(imdb250_data_zipped_file)
imdb250_data_items = list(imdb250_data)  

# Establishing Redis connection using environment variables (with Render details)
redis_url = 'redis://red-ct1cs63tq21c73enkkkg:6379'
parsed_url = urlparse(redis_url)
r = redis.StrictRedis(
    host=parsed_url.hostname,
    port=parsed_url.port,
    password=None,
    decode_responses=True,
    socket_timeout=30
)


# Creating a class for retrieving data for deployment
class Imdb250Data:
    def compute_cached_data(self, data_items: list[tuple]) -> pd.DataFrame:
        
        value, key = data_items
        
        json_data = value.to_json()            
        r.set(key, json_data)
        cached_data = pd.DataFrame(json.loads(json_data))  
        
        return cached_data

    
    def get_cached_data(self, data_items: list) -> pd.DataFrame:
        
        value, key = data_items
        cached_data = r.get(key)
        if cached_data:
                return pd.DataFrame(json.loads(cached_data))
        else:
                return self.compute_cached_data(data_items)

    # Method for fetching the IMDb 250 in a dataframe
    def imdb250(self) -> pd.DataFrame:
        return self.get_cached_data(imdb250_data_items[0])
    
    
    # Method for getting dataframe with similarity scores
    def imdb_250_similarities(self) -> pd.DataFrame:
        return self.get_cached_data(imdb250_data_items[1])
        
               
    # Method for getting recommendations based on user preference
    def get_recommendations(self, user_preferences: list) -> list:
        similarities_df = self.imdb_250_similarities()

        cross_df = similarities_df.reindex(similarities_df.columns)

        preferences_series = pd.concat([cross_df[preference]
                                        for preference in user_preferences]
                                       )
        ordered_series = preferences_series.sort_values(
            ascending = False).to_frame('score')
        filtered_series = ordered_series[
            ~(ordered_series.index.isin(user_preferences))]
        top_recommendations = filtered_series.query('score  >= .55')
        if len(top_recommendations) >= 5:
            return list(top_recommendations.index[:5])
        else:
            return list(filtered_series.index[:5])
