import requests

def get_tei_data(dhis2_base_url, dhis2_username, dhis2_password, BeneficiaryRegID, tei_data_cache):
    if BeneficiaryRegID in tei_data_cache:
        return tei_data_cache[BeneficiaryRegID]

    attribute_value = BeneficiaryRegID
    url = f"{dhis2_base_url}trackedEntityInstances.json?ouMode=ALL&program=vyQPQ07JB9M&fields=trackedEntityInstance,orgUnit&filter=HKw3ToP2354:EQ:{attribute_value}"
    response = requests.get(url, auth=(dhis2_username, dhis2_password))

    if response.status_code == 200:
        tei_data = response.json()
        if tei_data.get("trackedEntityInstances"):
            tei_data = tei_data["trackedEntityInstances"][0]
            tei_data_cache[BeneficiaryRegID] = tei_data
            return tei_data
        else:
            print(f"TEI data not found for BeneficiaryRegID: {BeneficiaryRegID}")
            return None
    else:
        print(f"Failed to fetch TEI data for BeneficiaryRegID: {BeneficiaryRegID}")
        return None

def construct_event_payload(tei_data, CreatedDate, BenCallID, CallType, CallTime, CallEndTime, CallDurationInSeconds, ReceivedRoleName, IsOutbound, Category, SubCategory):
    orgUnit = tei_data["orgUnit"]
    tei_uid = tei_data["trackedEntityInstance"]

    event_payload = {
        "program": "vyQPQ07JB9M",
        "orgUnit": orgUnit,
        "eventDate": CreatedDate,
        "programStage": "ISSSjurI0kD",
        "status": "COMPLETED",
        "trackedEntityInstance": tei_uid,
        "dataValues": [
            {"dataElement": "hsbXpo83f4I", "value": BenCallID},
            {"dataElement": "ioNKjuWD3s9", "value": CallType},
            {"dataElement": "Z3820wjWvkf", "value": CallTime},
            {"dataElement": "L2s4xeD05hE", "value": CallEndTime},
            {"dataElement": "ZTNtr3RK0kh", "value": CallDurationInSeconds},
            {"dataElement": "hUDunUrmF14", "value": ReceivedRoleName},
            {"dataElement": "IZ8umfwfXSm", "value": "false" if IsOutbound == 0 else "true"},
            {"dataElement": "sSWrwFFrd94", "value": Category},
            {"dataElement": "C5CFVWUYfeQ", "value": SubCategory}
        ]
    }
    return event_payload


def create_events_in_dhis2(dhis2_base_url, dhis2_username, dhis2_password, multiple_events_payload):
    response = requests.post(
        f"{dhis2_base_url}events",
        json=multiple_events_payload,
        auth=(dhis2_username, dhis2_password)
    )

    if response.status_code == 201:
        event_ids = [item.get("event") for item in response.json().get("response", {}).get("importSummaries", [])[0].get("imported")]
        print(f"Events created successfully. Event IDs: {event_ids}")
    else:
        print(f"Failed to create events. Error: {response.text}")
