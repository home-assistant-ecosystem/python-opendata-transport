"""
Copyright (c) 2015-2017 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
from opendata_transport import OpendataTransport

data = OpendataTransport('Bern', 'Biel')

# Get the data
data.get_data()

# Print the start and the destination name
print("Train connections:", data.from_name, "->", data.to_name)

# Print the next three connections
print(data.connections)

# Print the details of the next connection
print(data.connections[0])
