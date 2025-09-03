import sys
import base64
import json
import zlib
import pyperclip
base_blueprint_bottom = (
"0eNq1mV9r2zAUxb+LntVSXclOHFhhsOc9D0oJTqqtAv8JttOtlHz33XO1NWzLhlYh8tCjXxP5HPeKkzQvatcd/WEKw6I2Lyrsx2FWm7sXNYcvQ9uBDW3v1Ua1U1gee7+E/dV+7HdhaJdxUietwvDgv6mNOd1r5YclLMHHLWTxvB2O/c5P/AT9c6u5b7vuqmv7g9LqMM78knHApXgbsva60upZba5M464rvgB7Wqax2+78Y/sU+KL8zH2Y9sewbP3Q7jr/oDbLdPT6FfNLHl53/RymedmeAy3PB7h4CtNyZHK2Jc+4+qTiNeelxU0xWPSHdpK8G/UOvz7Onq/RjdMcr3w66T/ykv73rftn9HXzl+Dnvc4h5zek9O3+EUlmj222v+QdD57TijH1/uMHfu14XA7H/979dOm22KzbsnrbbTnHu7kQ2f6W+fZWXbTusqxXRazfpFmvsqzbEtapSbNeZ1k3Rayv06yvcqyvmiLWV2nW11nWixxTqtOsN1nWixxTqtKsm5ss72WG3SV6Nzne6zLTbhO9Z5V1XWbcKdF7VqPWZeY9sVFNVqXWZXopsVJNVqfWRc6qSexUk1WqVZGzahJL1WS1alXkrJrEVjVZtVoVmXeTWKsmq1erMvOe2KuU1auuzLwn9ipl9aorM++JvUpZveqKdJNJ7FXK6lVX5qwm9ipl9aorc1YTe5WyetUWOauJtUpZtWqLjHtiq1JWq9oi055YqpRVqrbIsCd2KmV1KhWZ9cRKtVmVSkVqKbFRbVajUpl/5CVazypUKvOBKdF6Vp9SmU5KtJ5Vp6bIrF9s03utvoZJvn+5M5r44e71HX5aUVYb7bQR5fBgxWtdCQOphPFa18J4zQqM13oljNeswHit18J4zQqM17oRxmtWYLzW3P9GpIMEBdH8lsZE7aCFG3CKXAzHHECa33qaqB20cMQyMRcQtHBEMzEbELRwxDMxHxC0cEQ0MSMQtHDENDEnELRwRDUxKxC0cMSlGBcIWv4OyEsxLxC0cOSlmBcIWjjyUswLBC0ceSnmBYIWjrwU8wJBC0deinmBoIUjL8W8rAlaOPJSzAsELRx5KeYFghaOvDbmBYKWaUNeG/MCQQtHXhvzAkELR14b8wJBC0de+2NukdciL896WHzPs3/+ClOrJz/NciKqmhrXNNXKVtat6HT6DkUwrIo="
)
base_blueprint_top = (
"0eNqtWdFq20AQ/Jd7vhTtnhVZhgYKfe5zoQQjO9dGYEtGktOG4H/vzl6IH1raa/fwy+xIOs3odhksvbjd4RxPUz8sbvPi+v04zG7z5cXN/behO4AbumN0G9dN/fJ4jEu/v9mPx10/dMs4uYt3/fAQf7gNXe69i8PSL31MS2jxvB3Ox12c5AT/56W8O42zXD0OuKusyM36Xe3ds9vccF3LnR76Ke7TCWvvROoyjYftLj52T70sIFddV97K4QddbcaBOaIGOS8dvFbejac4dWk5d3fnLpeL/0U0m0RTYdGUJzpYRK/awqI5T/TKJLopLDrkia5Nokv39CpP9K1JdCgsus4T3ZhElx7E2zzRa4voUHoQmzzRrUl06UFc54mmyqS6dFO3mapNmRiKx0tmKJIpFbl0X1NmLJIpF7l0Z1NmMJIpGbl0yFBmNJIpG7n0RFJmOJIpHbn4SGbGI5nykYqPZGZAkikhqXhvZ0YkmTKSivd2ZkiyKSSpeG9npiSbUrIq/n8m96+jKSWr0nHDmSnJppSsSo8kZ6Ykm1KyKj2SnJmSbErJqvRIcmZKsiUlqS3e25kpyY1JdvHezkxJXptkF+/tzJTk1iS7eG9npmSwpCSti8dNZkoGMsku/gItMyUDm2SXHsmQ+4o1mGQbR/JrP83L9vqKfnk+QclTPy1nYd6kpTNuYrd/xJv6v71P/vDpo1w7npfT+Z9X//1TuobyfOwOh5tDdzz9+dE0zTvs6e8ex76f9ud+2cah2x3ig9ss0zn6N/rtEf3HE/rs0j2vz0W28tRNupUb9x6Hz3OUexzGaU53vuCDx3fZRHzt+EKePHu694JWglaCpPZBOakFgZNaMCla4SdIal8rB6ZWTmp/q5zUgsBJ7RvlpBYETmq/Vk5qQeCk9q1yUgtiQVJ7qpRsIaDSM8F4oqS7Ak+Jhx169aOCkyNQnpInUMDKwxYlX6CAlYc1St5AASsPe5T8gQJWHhYpeQQFrDxsUvIJClh5WKXkFRSw8rDLyS4oYN0R+OXkFxSw8rp9yS/rBr7uIPzy6x7CLye/oDwnv6CAlYdfTn5BASsPv5z8ggJWHn45+QUFrDz8cvILClh5+OXkFxSw8vAbkl9QwNpt8BuSX1DAysNvSH5BASuvjRq0YwJ8yQTzvfR5v8SjDML1Y6F3T3GaddrqW25XbVs3oQ6rhi+Xnz6UbHw="
)

def blueprint_to_json(string):
    data = zlib.decompress(base64.b64decode(string[1:]))
    return json.loads(data)

def json_to_blueprint(json_data):
    compressed = zlib.compress(json.dumps(json_data).encode('utf-8'), level=9)
    return '0' + base64.b64encode(compressed).decode('utf-8')

def make_blueprint(blueprint, signal_list,top_or_bottom):
    j = 0
    if top_or_bottom == "bottom":
        j=-1
    k=-1
    if top_or_bottom == "bottom":
        k=32
    length = len(blueprint['blueprint'].get("entities", 0))
    for i, entity in enumerate(blueprint['blueprint']['entities']):

        if entity['name'] == "arithmetic-combinator":
            if "first_signal" not in entity['control_behavior']['arithmetic_conditions']:
                if top_or_bottom == "bottom":
                    k=k-1
                else:
                    k=k+1
                if len(signal_list["signals"]["decoder"]) > k:
                    if signal_list["signals"]["decoder"][k] == 0:

                        entity['control_behavior']['arithmetic_conditions']['first_signal'] = {
                            "constant": 0
                        }
                        entity['control_behavior']['arithmetic_conditions']['output_signal'] = {
                            "constant": 0
                    }
                    else:  
                        entity['control_behavior']['arithmetic_conditions']['first_signal'] = {
                            "type": "virtual",
                            "name": signal_list["signals"][top_or_bottom][index]
                        }
                        entity['control_behavior']['arithmetic_conditions']['output_signal'] = {
                        "type": "virtual",
                        "name": signal_list["signals"]["decoder"][k]
                        }
                    j=j+1
            else:
                j=j+1
    else:
        new_blueprint = json_to_blueprint(blueprint)
        pyperclip.copy(new_blueprint)
        print("Encoded Factorio Blueprint String has been copied to your clipboard!")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: generate_decoder.py <json_path> <index> <top_or_bottom>?  ")
    else:
        json_path = str((sys.argv[1]))
        index = int(sys.argv[2])
        top_or_bottom = (sys.argv[3])

        with open(json_path, 'r') as file:
            signal_list = json.load(file)

        if top_or_bottom == "top":
            base_blueprint=base_blueprint_top
        else:
            base_blueprint=base_blueprint_bottom
        make_blueprint(blueprint_to_json(base_blueprint),signal_list,top_or_bottom)
