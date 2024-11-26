import json

# Carregar o datadump original
with open('datadump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Organizar por modelo
games = [entry for entry in data if entry['model'] == 'games.games']
publishers = [entry for entry in data if entry['model'] == 'games.publisher']
users = [entry for entry in data if entry['model'] == 'users.user']
orders = [entry for entry in data if entry['model'] == 'checkout.order']

# Verificar se há duplicatas de PKs
def check_duplicates(entries, model_name):
    seen = set()
    duplicates = []
    for entry in entries:
        pk = entry['pk']
        if pk in seen:
            duplicates.append(pk)
        seen.add(pk)
    return duplicates

# Checar duplicatas em cada modelo
for model_name, entries in {
    'games.games': games,
    'games.publisher': publishers,
    'users.user': users,
    'checkout.order': orders,
}.items():
    duplicates = check_duplicates(entries, model_name)
    if duplicates:
        print(f"Duplicatas encontradas no modelo {model_name}: {duplicates}")

# Reorganizar os dados para evitar conflitos de dependências
# Primeiro carregamos publishers, depois jogos, usuários e pedidos
new_data = publishers + games + users + orders

# Salvar em um novo arquivo JSON
with open('datadump_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4, ensure_ascii=False)

print("Novo dump salvo como 'datadump_fixed.json'")
