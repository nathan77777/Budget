CREATE TABLE Categorie_produit(
    idCategorie INTEGER PRIMARY KEY ,
    Libelle VARCHAR(20)
);
CREATE TABLE Categorie_client(
    idClient INTEGER PRIMARY KEY,
    Libelle VARCHAR(30),
    Description VARCHAR(50)
);



INSERT INTO Categorie_produit (idCategorie, Libelle) VALUES
(1, 'Alimentation'),
(2, 'Électronique'),
(3, 'Vêtements'),
(4, 'Hygiène'),
(5, 'Loisirs'),
(6, 'Maison'),
(7, 'Papeterie');


INSERT INTO Categorie_client (idClient, Libelle, Description) VALUES
(1, 'Junior', 'entre 0 et 16 ans'),
(2, 'Jeune adulte', 'entre 17 et 30 ans'),
(3, 'Adulte', 'entre 31 et 60 ans'),
(4, 'Sénior', 'plus de 60 ans');
