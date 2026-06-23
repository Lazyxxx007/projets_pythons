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
            supprimer_aliment()
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

def tri_save(liste):
    liste.sort()
    ecriture_fichier(liste)

def afficher_courses():
    courses = ouverture_fichier()
    if not courses:
        print("Vous n'avez aucun aliment dans votre liste de courses")
        return
    tri_save(courses)
    for num, aliment in enumerate(courses, start=1):# enumerate permet de faire une liste notée avec la liste en argument et avec possibilité de définir le start avec enumerate(liste, start=?)
        print(f"{num} - {aliment}")
    
def ajouter_aliment(aliment):
    courses = ouverture_fichier()
    aliment = aliment.strip()
    while aliment == "":
        aliment = input("Veuillez saisir un aliment: ").strip()
    if aliment in courses:
        print("Cet aliment est déjà dans votre liste de courses")
    else:
        courses.append(aliment)
        ecriture_fichier(courses)
        print("Aliment ajouté avec succès! ")

def supprimer_aliment():
    courses = ouverture_fichier()
    afficher_courses()
    print(f"{len(courses) +1 } - Quitter")
    while True:
        try: 
            sup = int(input("Faites votre choix: "))
            while 1 > sup > len(courses)+1:
                sup = int(input("Veuillez choisir un numéro de la liste. "))
            if sup == len(courses) +1:
                return
            else:
                courses.pop(sup - 1)
                ecriture_fichier(courses)
                print("Aliment supprimé avec succès! ")
                return
        except ValueError:
            print("Assurez vous de taper une valeur entière")
        

accueil()