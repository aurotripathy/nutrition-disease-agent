# https://openfoodfacts.github.io/openfoodfacts-python/usage/

# also try https://go-upc.com/plans/api for code-to-name lookup

from openfoodfacts import API, APIVersion, Country, Environment, Flavor
import pprint   
import time


def get_nutriments_from_off(search_term: str) -> dict:
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


if __name__ == "__main__":
    search_term = "potato chips"
    nutriments = get_nutriments_from_off(search_term)
    print(f"\nSearch term: {search_term}")
    print("Nutriments:")
    pprint.pprint(nutriments)