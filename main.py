import os
import requests
from dotenv import load_dotenv
load_dotenv()

startggURL = "https://api.start.gg/gql/alpha"
key = os.getenv("STARTGG_KEY")

def get_slug(link: str) -> str:
    print (link[21:])
    return link[21:]

def get_id(slug: str) -> int:
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    graphql_query: str = """
    query getEventId($slug: String) {
        event(slug: $slug) {
            id
            name
        }
    }
    """
    
    payload: dict = {
        "query": graphql_query,
        "variables": {
            "slug": slug
        }
    }

    try:
        response = requests.post(startggURL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['data']['event']['id']

    except Exception as e:
        print(f"Error: {e}")
        return

def get_entrants(id: int) -> list[str]:
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    graphql_query: str = """
    query EventEntrants($id: ID!, $page: Int!, $perPage: Int!) {
        event(id: $id) {
            id
            name
            entrants(query: {
                page: $page
                perPage: $perPage
            }) {
                pageInfo {
                    total
                    totalPages
                }
                nodes {
                    id
                    participants {
                        id
                        gamerTag
                    }
                }
            }
        }
    }
    """
    
    payload: dict = {
        "query": graphql_query,
        "variables": {
            "id": id,
            "page": 1,
            "perPage": 50
        }
    }

    try:
        response = requests.post(startggURL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        entrants = data['data']['event']['entrants']['nodes']
        tags = []
        for entrant in entrants:
            tag = entrant['participants'][0]['gamerTag']
            tags.append(tag)

        return tags

    except Exception as e:
        print(f"Error: {e}")
        return

def main(link: str):
    slug = get_slug(link)
    id = get_id(slug)
    tags = get_entrants(id)
    print (tags)

link = "https://www.start.gg/tournament/spring-2026-rpi-smash-weekly-2/event/ultimate-singles"
main(link)
