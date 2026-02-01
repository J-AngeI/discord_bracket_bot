import os
import requests
from dotenv import load_dotenv
load_dotenv()

startggURL = "https://api.start.gg/gql/alpha"
key = os.getenv("STARTGG_KEY")

class Prediction:
    def __init__(self, name, prediction):
        self.name = name
        self.prediction = prediction
        self.accuracy = 0

Prediction = type('Prediction', (), {
    '__init__': lambda self, name, prediction: (
        setattr(self, 'name', name),
        setattr(self, 'prediction', prediction),
        setattr(self, 'accuracy', 0)
    )[0]
})

def get_slug(link: str) -> str:
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
        print(f"Error getting id: {e}")
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
            if len(entrant['participants']) == 0:
                continue
            tag = entrant['participants'][0]['gamerTag']
            tags.append(tag)

        return tags

    except Exception as e:
        print(f"Error getting entrants by id: {e}")
        return

def get_entrants_from_link(link: str) -> list[str]:
    slug = get_slug(link)
    id = get_id(slug)
    tags = get_entrants(id)

    return tags

def get_standings(id: int):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    graphql_query: str = """
    query EventStandings($id: ID!, $page: Int!, $perPage: Int!) {
        event(id: $id) {
            id
            name
            standings(query: {
                perPage: $perPage,
                page: $page
            }){
                nodes {
                    placement
                    entrant {
                        id
                        name
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
            "perPage": 8
        }
    }

    try:
        response = requests.post(startggURL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        standings = data['data']['event']['standings']['nodes']
        tags = []
        for entrant in standings:
            tag = entrant['entrant']['name']
            tags.append(tag)

        return tags

    except Exception as e:
        print(f"Error getting standings from id: {e}")
        return

def get_standings_from_link(link: str) -> list[str]:
    slug = get_slug(link)
    id = get_id(slug)
    standings = get_standings(id)

    return standings

def get_prediction_accuracy(id: int, prediction: Prediction) -> int:
    standings = get_standings(id)

    p_standings = prediction.prediction

    score = 0
    for i in range(0,8):
        if p_standings[i] == standings[i]:
            score += 12.5
            continue

        # Dont forget: 2 people get 5th and 7th, so swapping them still yeilds full points
        if i == 4 and p_standings[i] == standings[i+1]:
            score += 12.5
            continue
        if i == 5 and p_standings[i] == standings[i-1]:
            score += 12.5
            continue
        if i == 6 and p_standings[i] == standings[i+1]:
            score += 12.5
            continue
        if i == 7 and p_standings[i] == standings[i-1]:
            score += 12.5
            continue

        # This is an 80 / 20 split. 80 percent of the credit is based on if the people are in the top 8
        # The rest comes from the ordering.
        if p_standings[i] in standings:
            score += 10
            continue
    
    prediction.accuracy = score
    return score
