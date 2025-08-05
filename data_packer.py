import base64

if __name__ == "__main__":
    with open("./阳春村庄名录.txt", "rb") as file:
        data = base64.b64encode(file.read())

    with open("./data.py", "w") as file:
        file.write("raw_data = b\"")
        file.write(data.decode())
        file.write("\"")