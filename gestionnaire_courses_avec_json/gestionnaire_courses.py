#Defis

import json

#Charger une liste à partir de courses.json

def accueil():
    while True:
        print("===== COURSES =====")
        print("1 - Voir les courses")
        print("2 - Ajouter un aliment")
        print("3 - Supprimer un aliment")
        print("4 - Quitter")

        choix = input("Faites votre choix: ")
        if choix == "1":
            afficher_courses()
        elif choix == "2":
            aliment1 = input("Saisissez le nom de l'aliment que vous souhaitez ajouter: ")
            ajouter_aliment(aliment1)
        elif choix == "3":
            aliment2 = input("Saisissez le nom de l'aliment que vous souhaitez supprimer: ")
            supprimer_aliment(aliment2)
        elif choix == "4":
            break
        else:
            print("Choix incorrect")


def ouverture_fichier():
    with open("courses.json","r") as l:
        courses = json.load(l)
    return courses

def ecriture_fichier(courses):
    with open("courses.json","w") as l:
        json.dump(courses,l)

def afficher_courses():
    courses = ouverture_fichier()
    if not courses:
        print("Vous n'avez aucun aliment dans votre liste de courses")
        return
    for aliment in courses:
        print(aliment)
    
def ajouter_aliment(aliment):
    courses = ouverture_fichier()
    courses.append(aliment)
    ecriture_fichier(courses)
    print("Aliment ajouté avec succès! ")

def supprimer_aliment(aliment):
    courses = ouverture_fichier()
    courses.remove(aliment)
    ecriture_fichier(courses)
    print("Aliment supprimé avec succès! ")

accueil()