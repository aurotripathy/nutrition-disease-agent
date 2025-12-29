# https://openfoodfacts.github.io/openfoodfacts-python/usage/

# also try https://go-upc.com/plans/api for code-to-name lookup

from openfoodfacts import API, APIVersion, Country, Environment, Flavor
import pprint   
import time
import argparse
from collections import defaultdict
import logging

logging.basicConfig(level=logging.DEBUG)

def get_nutriments_from_open_food_facts(search_term: str) -> dict:
    """
        Fetches the nutriments for a given search-term from Open Food Facts
        using the Open Food Facts API.

        Args:
            search_term: A string representing the search term to search for.

        Returns:
            A dictionary of nutriments for the search term, or an empty dictionary if no nutriments are found.
        """
    api = API(
        user_agent="MyAwesomeApp/1.0",
        username="off",
        password="off",
        country=Country.us,
        flavor=Flavor.off,
        version=APIVersion.v2,
        environment=Environment.net, #staging server, not production
        timeout=10, # looks to be the minimum timeout
    )
    start_time = time.time()
    nutriments = {}
    try:
        # print(f"Searching Open Food Facts for {search_term}")
        result = api.product.text_search(search_term)
        
        # Append the search term to the file name when writing results
        # file_name = f"api_result_dump_{search_term}.txt"
        # with open(file_name, "w", encoding="utf-8") as f:
        #     pprint.pprint(result, stream=f)
        
        # Look in the "result" object for the 'products' list, then print the 'nutriments' for each product if present
        products = result.get('products', [])
        
        print(f"Looking for nutriments for: {search_term}")
        if products:
            nutriments = products[0].get('nutriments')
            if nutriments is None:
                print(f"No nutriments found for the product: {search_term}")
            else:
                print(f"Nutriments found for the product: {search_term}")
        else:
            print(f"No products found in the search result for: {search_term}")

    except Exception as e:
        print(f"Error searching products: {e}")
    finally:
        elapsed = time.time() - start_time
        print(f"API call took {elapsed:.2f} seconds")
    
    return nutriments


def group_nutriments(nutriments_dict: dict) -> dict:
    """
    Groups nutriments dictionary entries into a nested dictionary structure.
    
    Args:
        nutriments_dict: A dictionary of nutriments from Open Food Facts API.
    
    Returns:
        A nested dictionary where:
        - First level keys are the base nutrient names (before first delimiter)
        - Second level contains only entries with "_value", "_unit", and optionally "_serving"
    """
    # Step 1: Group entries by base name (before first "_")
    # Base name may contain '-' but should be extracted before the first '_'
    
    groups = defaultdict(dict)
    for key, value in nutriments_dict.items():
        if '_' in key:
            # Split by '_' first - base name is everything before first '_'
            # This allows base names like "saturated-fat" to be preserved
            base_name = key.split('_')[0]
        else:
            # No delimiters, use key as base name
            base_name = key

        groups[base_name][key] = value
    
    
    logging.debug(f"Grouped nutriments (by base name): {dict(groups)}")

    # Step 2 & 3: Filter each group to retain only _value, _unit, and _serving entries
    grouped_result = {}
    
    for base_name, group_items in groups.items():
        filtered_group = {}
        
        # Retain items containing "_value" and strip the base name prefix
        for key, value in group_items.items():
            if '_value' in key:
                # Remove the base_name prefix to get just "value"
                simplified_key = key.replace(f"{base_name}_", "")
                filtered_group[simplified_key] = value
        
        # Retain items containing "_unit" and strip the base name prefix
        for key, value in group_items.items():
            if '_unit' in key:
                # Remove the base_name prefix to get just "unit"
                simplified_key = key.replace(f"{base_name}_", "")
                filtered_group[simplified_key] = value
        
        # Retain items ending with "_serving" and strip the base name prefix
        for key, value in group_items.items():
            if key.endswith('_serving'):
                # Remove the base_name prefix to get just "serving"
                simplified_key = key.replace(f"{base_name}_", "")
                filtered_group[simplified_key] = value
        
        # Only add the group if it has at least one filtered entry
        if filtered_group:
            grouped_result[base_name] = filtered_group
    
    return grouped_result

def get_nutriments_from_off_grouped(search_term: str) -> dict:
    """
        Fetches the nutriments for a given search-term from Open Food Facts
        using the Open Food Facts API.

        Args:
            search_term: A string representing the search term to search for.

        Returns:
            A dictionary of nutriments for the search term, or an empty dictionary if no nutriments are found.
        """

    nutriments = get_nutriments_from_open_food_facts(search_term)
    return group_nutriments(nutriments)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get nutriments from Open Food Facts')
    parser.add_argument('search_term', type=str, help='Search term for the food product')
    args = parser.parse_args()
    
    search_term = args.search_term
    
    print("Getting nutriments from Open Food Facts and grouping them:")   
    grouped_nutriments = get_nutriments_from_off_grouped(search_term)
    print(f'Grouped nutriments type: {type(grouped_nutriments)}')
    for nutrient_name, nutrient_data in grouped_nutriments.items():
        print(f"{nutrient_name}: {nutrient_data}\n")

    print("Getting nutriments from Open Food Facts flat (un-grouped), one line per nutrient:")
    nutriments = get_nutriments_from_open_food_facts(search_term)
    for nutrient_name, nutrient_data in nutriments.items():
        print(f"{nutrient_name}: {nutrient_data}")