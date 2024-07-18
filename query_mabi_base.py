import requests
from mongodb_ah import *

def craft_request_body(item_id, item_last_match):
    request_body = [{
        "operationName": "auctionHouseSearch",
        "variables": {
          "server": "mabius6",
          "filters": [
            {
              "type": "ItemId",
              "comparator": "eq",
              "value": f"{item_id}"
            },
            {
              "type": "ListedAfter",
              "value": f"{item_last_match}"
            }
          ],
          "pagination": {
            "pageSize": 25,
            "pageIndex": 0
          },
          "sort": {
            "attribute": "ItemPrice",
            "direction": "Ascending"
          }
        },
        "extensions": {
          "persistedQuery": {
            "version": 1,
            "sha256Hash": "e42f50b9ab00b0e7b820afbaae91c07722178ed6b0d3aa3b578c8cc4edfe3a84"
          }
        }
      }]
    return request_body

def query_item_from_mabi_base(item_id, item_last_match):
    api_url="https://api.na.mabibase.com/graphql?t=1"
    request_body = craft_request_body(item_id, item_last_match)
    response     = requests.post(api_url, json=request_body)
    return response