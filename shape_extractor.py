import requests
import json

# You'll need to set this with your actual access token
ACCESS_TOKEN = "eyJraWQiOiIyMDI0MDkwMjA4NDIiLCJhbGciOiJSUzI1NiJ9.eyJpYW1faWQiOiJJQk1pZC02OTEwMDBDNjJEIiwiaWQiOiJJQk1pZC02OTEwMDBDNjJEIiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiYWUzZTA2NjUtNzkwZS00MjgzLWI1NDMtYmYzN2MzYmVmODZmIiwiaWRlbnRpZmllciI6IjY5MTAwMEM2MkQiLCJnaXZlbl9uYW1lIjoiUHJhbmF2IiwiZmFtaWx5X25hbWUiOiJSYWptYW5lIiwibmFtZSI6IlByYW5hdiBSYWptYW5lIiwiZW1haWwiOiJwcmFuYXYucmFqbWFuZWVAZ21haWwuY29tIiwic3ViIjoicHJhbmF2LnJham1hbmVlQGdtYWlsLmNvbSIsImF1dGhuIjp7InN1YiI6InByYW5hdi5yYWptYW5lZUBnbWFpbC5jb20iLCJpYW1faWQiOiJJQk1pZC02OTEwMDBDNjJEIiwibmFtZSI6IlByYW5hdiBSYWptYW5lIiwiZ2l2ZW5fbmFtZSI6IlByYW5hdiIsImZhbWlseV9uYW1lIjoiUmFqbWFuZSIsImVtYWlsIjoicHJhbmF2LnJham1hbmVlQGdtYWlsLmNvbSJ9LCJhY2NvdW50Ijp7InZhbGlkIjp0cnVlLCJic3MiOiJlZTQxNWMyMWI1NDM0N2UxOGJiYTY0NjU1Y2U1NTc5ZCIsImltc191c2VyX2lkIjoiMTI2OTQzNjUiLCJmcm96ZW4iOnRydWUsImltcyI6IjI4MTk3NDUifSwiaWF0IjoxNzI2OTgwNTM4LCJleHAiOjE3MjY5ODQxMzgsImlzcyI6Imh0dHBzOi8vaWFtLmNsb3VkLmlibS5jb20vaWRlbnRpdHkiLCJncmFudF90eXBlIjoidXJuOmlibTpwYXJhbXM6b2F1dGg6Z3JhbnQtdHlwZTphcGlrZXkiLCJzY29wZSI6ImlibSBvcGVuaWQiLCJjbGllbnRfaWQiOiJkZWZhdWx0IiwiYWNyIjoxLCJhbXIiOlsicHdkIl19.r3hq3d0om4-wVy5NhulkMoiKgxJTpderrmuhgPNyzaJ0P3RqGKR26DpcoGiLa5OSLvwMbP-6kMmjmC6M9N5_RpeaMdq4ZF_jLDo7d0Vk9iEzRxRPHvKDs72HAG5Vwwvr-sVDxrHLrtebSMjTmJ7ORA3IciYi6PeF5FXGM0UYpsU59vR-nvpSEQz68QvgpZUm3THrn-e0fqIIu4T80Yrzen2CXQBlDSEBqaVbqj4_RXjX0xKsMz6QY9-oZ-Wfe_JIzq8uqYdlVyfQC6XZpOpXpDAiiwgoE-jcjmaO99X18XRc4RgWe1aTw08zIS-JxNaOXofZWK0F3xpRDW_1eW-t4w"

def get_llm_response(prompt):
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    
    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 150,
            "repetition_penalty": 1
        },
        "model_id": "ibm/granite-3b-code-instruct",
        "project_id": "811c773e-6574-499a-811e-7f471622e5a1"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return data['results'][0]['generated_text'].strip()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

def get_shape_properties_from_llm(shape_input):
    initial_prompt = f"""Given a shape description for a cylinder or sphere, provide the shape properties in a structured format. If any required properties are missing, ask for them. Required properties for a sphere are shape, centre_x, centre_y, centre_z, and radius. For a cylinder, also include height.

Example input: sphere with radius 5 centered at 1, 2, 3
Example output:
shape = sphere
centre_x = 1
centre_y = 2
centre_z = 3
radius = 5

Example input: cylinder of radius 3 at origin
Example output:
shape = cylinder
centre_x = 0
centre_y = 0
centre_z = 0
radius = 3
What is the height of the cylinder?

Now, parse this input: {shape_input}
Output:"""

    llm_output = get_llm_response(initial_prompt)
    
    while "What is" in llm_output or "Please provide" in llm_output:
        print(llm_output)
        user_input = input("Your response: ")
        llm_output = get_llm_response(f"{initial_prompt}\n\n{llm_output}\n\nUser: {user_input}\n\nOutput:")
    
    return llm_output

def parse_llm_output(llm_output):
    properties = {}
    for line in llm_output.split('\n'):
        if '=' in line:
            key, value = line.split('=')
            properties[key.strip()] = value.strip()
    
    shape = properties.get('shape', '')
    centre_x = float(properties.get('Centre_x', 0))
    centre_y = float(properties.get('Centre_y', 0))
    centre_z = float(properties.get('Centre_z', 0))
    radius = float(properties.get('radius', 0))
    height = float(properties.get('height', 0)) if shape == 'cylinder' else None
    
    return [shape, centre_x, centre_y, centre_z, radius, height]

def get_shape_properties():
    print("Interactive Shape Properties Extractor (for cylinder and sphere)")
    print("You can describe the shape in natural language.")
    print("Example: 'sphere with radius 5 centered at 1, 2, 3'")
    print("         'cylinder of radius 3 at origin'")
    
    shape_input = input("\nPlease describe the shape: ")
    
    print("\nProcessing your input...")
    llm_output = get_shape_properties_from_llm(shape_input)
    
    print("\nExtracted properties:")
    print(llm_output)
    
    properties = parse_llm_output(llm_output)
    
    print("\nOutput list:")
    print(properties)
    
    return properties

if __name__ == "__main__":
    properties = get_shape_properties()
    
    print("\nYou can use this list in your Python code like this:")
    print("shape, centre_x, centre_y, centre_z, radius, height = properties")
    
    if properties[0] == "sphere":
        print("\nNote: For a sphere, the 'height' value will be None.")

