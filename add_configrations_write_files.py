import json
import hashlib
import itertools
import yaml
import os


# Funktion för att skapa en hash för en given kombination
def create_hash(combination):  # "Combination" är en dictionary med en specifik kombination av hyperparametrar
    comb_str = json.dumps(combination, sort_keys=True)
    return hashlib.sha256(comb_str.encode()).hexdigest()  # Returnerar en unik hash kod för den kombinationen


# Läs in redan gjorda kombinationer från en fil.
def load_done_combinations(filename):
    try:
        with open(filename,
                  'r') as f:  # Laddar in en fil i json format där både hash koden och hyperparametrarna för varja hash är sparat.
            return json.load(f)
    except FileNotFoundError:
        return {}  # retunerar en tom fil om filnamnet som gavs inte redan finns
    except json.JSONDecodeError:
        return {}


# Sparar den nya combinationen i json format till filen. Tar in en dictonary med hash och hyperparametrar.
def save_combinations(filename, combination_H):
    with open(filename, 'w') as f:
        json.dump(combination_H, f, indent=4)


# Tar in en dict med de önskade hyperparametrarna och dess värden. Skapar alla möjliga kombinationer och retunerar.
def generate_combinations(hyperparameters):
    keys = hyperparameters.keys()
    values = (param["values"] for param in hyperparameters.values())
    for combination in itertools.product(*values):
        yield dict(zip(keys, combination))


# Kollar om kombinationen redan körts, om inte så sapas en config fil och ett jobscript.
def add_combination_if_not_exists(new_combination, filename, index, name, template, configuration_files):
    done_combinations = load_done_combinations(filename)  # Läser in json fil med alla befintliga kombinationer.
    comb_hash = create_hash(new_combination)  # Generera en unik hash för den ny a kombinationen.
    if comb_hash in done_combinations:  # Kolla om konbinationen redan finns
        print("Kombinationen finns redan. \n" )
    else:
        write_files(new_combination, name, index, configuration_files, template)
        done_combinations[comb_hash] = new_combination
        save_combinations(filename, done_combinations)
        print("Kombinationen har lagts till.\n")


# Writes new configuration files from a template and saves the files in a folder. Creates jobscripts for each configuration.
def write_files(combination, name, index, configurations_folder, template):
    # Write configuration file
    filename_conf = f"{name}_{index}.yaml"
    if not os.path.exists(configurations_folder):
        os.makedirs(configurations_folder)
    output_path_config = os.path.join(configurations_folder, filename_conf)

    with open(template, 'r') as f1, open(output_path_config, 'w') as f2:
        f2.write(f"# Configuration {index} written to {filename_conf}\n")
        f2.write(f"run_name: {name}_{index}\n")
        f2.write(f"root: results/{name}\n")
        for line in f1:
            f2.write(line)
        f2.write("\n")
        yaml.dump(combination, f2)

def main(hyperparameters, filename, name, template, configuration_files):
    # Hyperparameters är en dictionary med vilka hyperparametrar som ska varieras och en lista med de värden som ska testas.
    # Filename är en json fil med de parametrar som redan körts.
    # Name är det önskade namnet på svepet, här är det viktigt att välja ett unikt namn så at inte körningarna blandas ihop i wandbai
    # Template är en .yaml som configurationsfilerna ska utgå ifrån.
    i = 1
    for combinations in generate_combinations(hyperparameters):
        add_combination_if_not_exists(combinations, filename, i, name, template, configuration_files)
        i = i + 1


hyperparameters_allegro = {
    "parity": {"values": ["o3_full", "o3_restricted", "so3"]},
    "l_max": {"values": [3, 2, 1]},
    "r_max": {"values": [5.5, 5, 4.5, 4, 3.5, 3]},
    "num_layers": {"values": [1, 2, 3]},
    "env_embed_multiplicity":  {"values": [1, 8, 32, 64]}, # num_features in NequIP
    "num_basis": {"values": [4, 8, 10]},
}

filename = "hyperparameter_combinations_allegro.json"

main(hyperparameters_allegro, filename, "Allegro_stress", "Base.yaml", "configuration_folder")
