#Gestionnaire de bibliothèque

def accueil(bibliotheques):
    while True:
        print("===== BIBLIOTHÈQUE =====")
        print("1 - Ajouter un livre")
        print("2 - Afficher tous les livres")
        print("3 - Rechercher un livre")
        print("4 - Supprimer un livre")
        print("5 - Modifier un livre")
        print("6 - Afficher les livres d'un auteur")
        print("7 - Afficher les livres d'un genre")
        print("8 - Afficher les livres disponibles")
        print("9 - Emprunter un livre")
        print("10 - Retourner un livre")
        print("11 - Statistiques")
        print("12 - Quitter")

        choix = input("Faites votre choix: ")
        if choix == "1":
            titre = input("Saisissez le titre du livre: ")
            auteur = input("Saisissez le nom de l'auteur qui a écrit le livre: ")
            annee = int(input("Veuillez entrer l'année de parution de ce livre: "))
            genre = input("Quel est le genre de ce livre: ")
            pages = int(input("Combien de pages contient ce livre: "))
            disponible = input("Ce livre est il disponible? ")
            if livre_existe(titre, bibliotheques):
                print("Ce livre existe déjà")
            else:
                livre=creer_livre(titre,auteur,annee,genre,pages,disponible)
                bibliotheques.append(livre)
        elif choix == "2":
            afficher_liste(bibliotheques)
        elif choix == "3":
            nom = input("Saisissez le titre du livre que vous recherchez: ")
            rechercher_livre(nom, bibliotheques)
        elif choix == "4":
            nom1 = input("Saisissez le titre du livre que vous souhaitez supprimer: ")
            supprimer_livre(nom1, bibliotheques)
        elif choix == "5":
            titre_livre = input("Quel livre souhaitez vous modifier? ")
            for liv in bibliotheques:
                if titre_livre == liv["titre"]:
                    modifier_livre(liv)
            print(f"Nous ne possédons pas ce livre")
        elif choix == "6":
            nom_auteur = input("Saisissez le nom de l'auteur dont vous souhaitez affichez les livres: ")
            afficher_liste(afficher_livre_auteurs(nom_auteur, bibliotheques))
        elif choix == "7":
            nom_genre = input("Saisissez le genre des livres que vous souhaitez afficher: ")
            afficher_liste(afficher_livre_genre(nom_genre, bibliotheques))
        elif choix == "8":
            f = afficher_livre_disponible(bibliotheques)
            print("Voici nos livres disponibles: ")
            afficher_liste(f)
        elif choix == "9":
            nom2 = input("Saisissez le titre du livre que vous souhaitez emprunter: ")
            emprunter_livre(nom2,bibliotheques)
        elif choix == "10":
            nom3 = input("Saisissez le titre du livre que vous souhaitez retourner: ")
            retourner_livre(nom3,bibliotheques)
        elif choix == "11":
            statistiques(bibliotheques)
        elif choix == "12":
            break
        else:
            print("Choix invalide")

def creer_livre(titre, auteur, annee, genre, pages, disponible):
    livre ={
        "titre" : titre,
        "auteur": auteur,
        "annee": annee,
        "genre": genre,
        "pages": pages,
        "disponible": disponible
    }
    return livre

def afficher_livre(livre):
    print(f"Titre: {livre['titre']} | Auteur: {livre['auteur']} | Année de publication: {livre['annee']} | Genre: {livre['genre']} | Nombres de pages: {livre['pages']} | Disponibilité: {livre['disponible']} ")

def livre_existe(titre, liste):
    if not liste:
        return False
    for livre in liste:
        if livre["titre"] == titre:
            return True
    return False

def afficher_liste(liste):
    if not liste:
        print("Liste vide")
        return
    for livre in liste:
        afficher_livre(livre)

def rechercher_livre(titre, liste):
    if not liste:
        print("Liste vide")
        return None
    for livre in liste:
        if livre["titre"] == titre:
            if livre["disponible"] == "Oui":
                print(f"Nous possédons le livre intitulé {titre} et il est disponible ") 
            else:
                print(f"Nous possédons le livre intitulé {titre} mais il est actuelllement indisponible ")
            return
    print(f"Nous ne possédons pas ce livre")

def supprimer_livre(titre, liste):
    if not liste:
        print("Liste vide")
        return None
    for livre in liste:
        if livre["titre"] == titre:
            liste.remove(livre)
            print("Livre supprimé avec succès")
            return
    print("Ce livre n'existe pas dans notre bibliothèque")

def modifier_titre(titre, livre):
    livre["titre"]=titre

def modifier_auteur(auteur, livre):
    livre["auteur"]=auteur

def modifier_annee(annee, livre):
    livre["annee"]=annee

def modifier_genre(genre, livre):
    livre["genre"]=genre

def modifier_pages(pages, livre):
    livre["pages"]=pages

def modifier_livre(livre):
    while True:
        print("Que souhaitez vous modifier?")
        print("A - Le titre")
        print("B - L'auteur")
        print("C - Le genre")
        print("D - L'année de publication")
        print("E - Le nombre de pages")
        print("F - Retour en arrière")
        choix = input("Faites votre choix: ")
        if choix=="A":
            titre = input("Saisissez le nouveau titre: ")
            modifier_titre(titre,livre)
        elif choix=="B":
            auteur = input("Saisissez le nouveau nom de l'auteur: ")
            modifier_auteur(auteur,livre)
        elif choix=="C":
            genre = input("Saisissez le genre: ")
            modifier_genre(genre,livre)
        elif choix=="D":
            annee = int(input("Saisissez à nouveau l'année de publication: "))
            modifier_annee(annee,livre)
        elif choix=="E":
            pages = int(input("Saisissez le nombre de pages: "))
            modifier_pages(pages,livre)
        elif choix=="F":
            return
        else:
            print("Faites un choix valide")

def afficher_livre_auteurs(auteur, livres):
    if not livres:
        print("Liste vide !")
        return
    l = []
    for livre in livres:
        if livre["auteur"] == auteur:
            l.append(livre)
    return l

def afficher_livre_genre(genre, livres):
    if not livres:
        print("Liste vide !")
        return
    l = []
    for livre in livres:
        if livre["genre"] == genre:
            l.append(livre)
    return l

def afficher_livre_disponible(livres):
    if not livres:
        print("Liste vide !")
        return
    l = []
    for livre in livres:
        if livre["disponible"] == "Oui":
            l.append(livre)
    return l
        
def emprunter_livre(titre,livres):
    if not livres:
        print("Liste vide !")
        return
    for livre in livres:
        if livre["titre"] == titre:
            if livre["disponible"] == "Oui":
                livre["disponible"] = "Non"
                print("Livre emprunté avec succès! ")
                return
            else:
                print("Malheureusement, ce livre a déjà été emprunté! ")
                return
    print("Nous ne possédons pas ce livre! ")

def retourner_livre(titre,livres):
    if not livres:
        print("Liste vide !")
        return
    for livre in livres:
        if livre["titre"] == titre:
            livre["disponible"] = "Oui"
            print("Livre retourné avec succès! ")
            return
    print("Navré ce livre ne vient pas de chez nous, pour le retourné il va falloir l'ajouter à notre bibliothèque ")

def maximum_pages(livres):
    if not livres:
        print("Liste vide !")
        return
    max_pages = livres[0]["pages"]
    titre = livres[0]["titre"]
    for livre in livres:
        if livre["pages"] > max_pages:
            max_pages = livre["pages"]
            titre = livre["titre"]
    return titre

def ancien_livre(livres):
    if not livres:
        print("Liste vide !")
        return
    min_annee = livres[0]["annee"]
    titre = livres[0]["titre"]
    for livre in livres:
        if livre["annee"] < min_annee:
            min_annee = livre["annee"]
            titre = livre["titre"]
    return titre

def tous_genre(livres):
    if not livres:
        print("Liste vide !")
        return
    l=[]
    for livre in livres:
         if livre["genre"] not in l:
            l.append(livre["genre"])
    return l

def moyenne(livres):
    if not livres:
        return 0
    l = []
    for livre in livres:
        l.append(livre["pages"])
    return sum(l) / len(l)

def statistiques(livres):
    if not livres:
        print("Liste vide !")
        return
    taille = len(livres)
    print(f"Nombre total de livres: {taille}")
    l = afficher_livre_disponible(livres)
    taille_l= len(l)
    print(f"Nombre disponible: {taille_l}")
    print(f"Nombre empruntés: {taille - taille_l}")
    l1 = tous_genre(livres)
    taille_l1 = len(l1)
    print(f"Nombre de genre: {taille_l1}")
    max_pages = maximum_pages(livres)
    print(f"Livre ayant le plus de pages: {max_pages}")
    vieux_livre = ancien_livre(livres)
    print(f"Livre le plus ancien: {vieux_livre}")
    print(f"Moyenne du nombre de pages: {moyenne(livres)}")
    
bibliotheque = [
    {
        "titre": "Le Petit Prince",
        "auteur": "Antoine de Saint-Exupéry",
        "annee": 1943,
        "genre": "Roman",
        "pages": 96,
        "disponible": "Oui"
    },
    {
        "titre": "1984",
        "auteur": "George Orwell",
        "annee": 1949,
        "genre": "Science-fiction",
        "pages": 328,
        "disponible": "Non"
    },
    {
        "titre": "Harry Potter à l'école des sorciers",
        "auteur": "J.K. Rowling",
        "annee": 1997,
        "genre": "Fantasy",
        "pages": 320,
        "disponible": "Oui"
    },
    {
        "titre": "Le Seigneur des Anneaux",
        "auteur": "J.R.R. Tolkien",
        "annee": 1954,
        "genre": "Fantasy",
        "pages": 1216,
        "disponible": "Non"
    },
    {
        "titre": "L'Étranger",
        "auteur": "Albert Camus",
        "annee": 1942,
        "genre": "Roman",
        "pages": 184,
        "disponible": "Oui"
    },
    {
        "titre": "Les Misérables",
        "auteur": "Victor Hugo",
        "annee": 1862,
        "genre": "Roman",
        "pages": 1463,
        "disponible": "Oui"
    },
    {
        "titre": "Le Comte de Monte-Cristo",
        "auteur": "Alexandre Dumas",
        "annee": 1844,
        "genre": "Aventure",
        "pages": 1276,
        "disponible": "Non"
    },
    {
        "titre": "Da Vinci Code",
        "auteur": "Dan Brown",
        "annee": 2003,
        "genre": "Thriller",
        "pages": 592,
        "disponible": "Oui"
    },
    {
        "titre": "Dune",
        "auteur": "Frank Herbert",
        "annee": 1965,
        "genre": "Science-fiction",
        "pages": 688,
        "disponible": "Oui"
    },
    {
        "titre": "La Peste",
        "auteur": "Albert Camus",
        "annee": 1947,
        "genre": "Roman",
        "pages": 308,
        "disponible": "Non"
    },
    {
        "titre": "Le Rouge et le Noir",
        "auteur": "Stendhal",
        "annee": 1830,
        "genre": "Roman",
        "pages": 576,
        "disponible": "Oui"
    },
    {
        "titre": "Fondation",
        "auteur": "Isaac Asimov",
        "annee": 1951,
        "genre": "Science-fiction",
        "pages": 296,
        "disponible": "Oui"
    },
    {
        "titre": "Le Hobbit",
        "auteur": "J.R.R. Tolkien",
        "annee": 1937,
        "genre": "Fantasy",
        "pages": 310,
        "disponible": "Non"
    },
    {
        "titre": "L'Alchimiste",
        "auteur": "Paulo Coelho",
        "annee": 1988,
        "genre": "Roman",
        "pages": 208,
        "disponible": "Oui"
    },
    {
        "titre": "Les Trois Mousquetaires",
        "auteur": "Alexandre Dumas",
        "annee": 1844,
        "genre": "Aventure",
        "pages": 704,
        "disponible": "Oui"
    }
]

accueil(bibliotheque)


            



