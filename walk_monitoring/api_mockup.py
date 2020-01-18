from flask import Flask
import os
import random
import json

app = Flask(__name__)

user_id_paths = [os.path.join(app.root_path, 'data', str(i)) for i in range(1, 7)]
json_files = [os.listdir(user_id_paths[i]) for i in range(6)]
for dir in json_files:
    random.shuffle(dir)

data_pointers = [[0, len(l)] for l in json_files]


def get_json_file(my_id):
    my_id = my_id - 1
    pointer = data_pointers[my_id][0]
    length = data_pointers[my_id][1]
    if pointer + 1 == length:
        data_pointers[my_id][0] = 0
    json_path = os.path.join(user_id_paths[my_id], json_files[my_id][pointer], )
    data_pointers[my_id][0] += 1
    with open(json_path, 'r') as f:
        return json.loads(f.read())


@app.route("/")
def home():
    return 'asd'


@app.route("/1")
def id1():
    my_id = 1
    return get_json_file(my_id)


@app.route("/2")
def id2():
    my_id = 2
    return get_json_file(my_id)


@app.route("/3")
def id3():
    my_id = 3
    return get_json_file(my_id)


@app.route("/4")
def id4():
    my_id = 4
    return get_json_file(my_id)


@app.route("/5")
def id5():
    my_id = 5
    return get_json_file(my_id)


@app.route("/6")
def id6():
    my_id = 6
    return get_json_file(my_id)


if __name__ == "__main__":
    app.run(debug=True)
