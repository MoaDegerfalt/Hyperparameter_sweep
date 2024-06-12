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
def add_combination_if_not_exists(new_combination, filename, index, name, template):
    done_combinations = load_done_combinations(filename)  # Läser in json fil med alla befintliga kombinationer.
    comb_hash = create_hash(new_combination)  # Generera en unik hash för den ny a kombinationen.
    if comb_hash in done_combinations:  # Kolla om konbinationen redan finns
        print("Kombinationen finns redan. \n" )
    else:
        write_files(new_combination, name, index, "jobbsctipts", "configuration_files", template)
        done_combinations[comb_hash] = new_combination
        save_combinations(filename, done_combinations)
        print("Kombinationen har lagts till.\n")


# Writes new configuration files from a template and saves the files in a folder. Creates jobscripts for each configuration.
def write_files(combination, name, index, jobbscript_folder, configurations_folder, template):
    # Write configuration file
    filename_conf = f"{name}_{index}.yaml"
    if not os.path.exists(configurations_folder):
        os.makedirs(configurations_folder)
    output_path_config = os.path.join(configurations_folder, filename_conf)

    with open(template, 'r') as f1, open(output_path_config, 'w') as f2:
        f2.write(f"# Configuration {index} written to {filename_conf}\n")
        f2.write(f"run_name: {name}_{index}\n")
        for line in f1:
            f2.write(line)
        f2.write("\n")
        yaml.dump(combination, f2)

    # Write the jobscript
    if not os.path.exists(jobbscript_folder):
        os.makedirs(jobbscript_folder)
    filename_jobb = 'jobscript_' + str(name) + '_' + str(index)
    output_path_jobb = os.path.join(jobbscript_folder, filename_jobb)

    with open(output_path_jobb, 'w') as f:
        f.write('#!/usr/bin/env bash\n')
        f.write('#SBATCH -A NAISS2023-3-31 -p alvis\n')
        f.write('#SBATCH -N 1 --gpus-per-node=T4:1 \n')
        f.write('#SBATCH -t 0-02:00:00\n\n\n')
        f.write(
            'apptainer exec nequip.sif nequip-train ' + "/mimer/NOBACKUP/groups/ltu-fy/Moa/" + configurations_folder + "/" + filename_conf + '\n')


def main(hyperparameters, filename, name, template):
    # Hyperparameters är en dictionary med vilka hyperparametrar som ska varieras och en lista med de värden som ska testas.
    # Filename är en json fil med de parametrar som redan körts.
    # Name är det önskade namnet på svepet, här är det viktigt att välja ett unikt namn så at inte körningarna blandas ihop i wandbai
    # Template är en .yaml som configurationsfilerna ska utgå ifrån.
    i = 1
    for combinations in generate_combinations(hyperparameters):
        add_combination_if_not_exists(combinations, filename, i, name, template)
        i = i + 1


hyperparameters = {
    "invariant_layers": {"values": [4, 3, 2, 1]},
    "invariant_neurons": {"values": [128, 96, 64, 32]},
    "num_layers": {"values": [10, 8, 6, 4, 3, 2, 1]},
    "parity": {"values": [True, False]},
    "l_max": {"values": [3, 2, 1]},
    "num_features": {"values": [40, 30, 20, 10]},  
    "num_basis": {"values": [10, 8, 6, 4]},
    "use_sc": {"values": [True]},
}

filename = "hyperparameter_combinations_2.json"

main(hyperparameters, filename, "sweep_test", "Base.yaml")
