CREATE DATABASE Budget;

USE Budget;


CREATE TABLE Departements (
    Deptno INTEGER PRIMARY KEY AUTO_INCREMENT,
    NameDept VARCHAR(50)
);

CREATE TABLE Employes (
    Empno INTEGER PRIMARY KEY AUTO_INCREMENT,
    NameEmp VARCHAR(50)
);

-- Role de chaque Departement:
CREATE TABLE Roles (
    Deptno INTEGER PRIMARY KEY AUTO_INCREMENT,
    Executer BOOLEAN,
    Writer BOOLEAN,
    Reader BOOLEAN
);


--------------------------------------------------------------------------

-- Concernant les flux externes:
CREATE TABLE Categories(
    idCategory INTEGER PRIMARY KEY AUTO_INCREMENT,
    typeCategorie INTEGER,
    Descriptions VARCHAR(100),
    CHECK (typeCategorie IN (0,1))
);


--------------------------------------------------------------------------
-- Concernant les previsions & realisations:

CREATE TABLE Previsions(
    idPrevision INTEGER PRIMARY KEY AUTO_INCREMENT,
    deptno INTEGER,
    isValid BOOL,
    libelle VARCHAR(100),
    idCategory INTEGER,
    dateOperation DATE,
    montant FLOAT,
    FOREIGN KEY(idCategory) REFERENCES Categories(idCategory)
);


CREATE TABLE Realisations(
    idRealisation INTEGER PRIMARY KEY AUTO_INCREMENT,
    deptno INTEGER,
    isValid BOOL,
    libelle VARCHAR(100),
    idCategory INTEGER,
    dateOperation DATE,
    montant FLOAT,
    FOREIGN KEY(idCategory) REFERENCES Categories(idCategory)
);

--------------------------------------------------------------------------

CREATE TABLE soldeDebut(
    idDepartement INTEGER,
    anne INTEGER,
    montant FLOAT,
    FOREIGN KEY(idDepartement) REFERENCES Departements(Deptno)
);

create table CRM
(
    idCRM int auto_increment primary key,
    idClient int NOT NULL,
    idProduct int NOT NULL,
    dateCRM date,
    montant FLOAT
);

--------------------------------------------------------------------------

CREATE TABLE clients(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(20),
    prenoms VARCHAR(20)
);



CREATE TABLE categorie_tickets(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    descriptions VARCHAR(20)
);



CREATE TABLE tickets(
    id INTEGER PRIMARY key AUTO_INCREMENT,
    id_client INTEGER,
    priorite INTEGER,
    categorie_ticket INTEGER,
    objet VARCHAR(20),
    date_creation DATETIME,
    FOREIGN KEY(id_client) REFERENCES clients(id),
    FOREIGN KEY(priorite) REFERENCES priorites(id),
    FOREIGN KEY(categorie_ticket) REFERENCES categorie_tickets(id)
);


CREATE TABLE statuts_tickets(
    id INTEGER AUTO_INCREMENT PRIMARY key,
    descriptions VARCHAR(20)
);


CREATE TABLE historique_statuts_tickets(
    id_ticket INTEGER,
    id_statuts INTEGER,
    FOREIGN key(id_ticket) REFERENCES tickets(id)
    FOREIGN key(id_statuts) REFERENCES statuts_tickets(id)
);


CREATE TABLE historique_affectation_tickets(
    id_ticket INTEGER,
    id_employee INTEGER DEFAULT NULL,
    id_department INTEGER DEFAULT NULL,
    id_attributeur INTEGER,
    FOREIGN key id_employee REFERENCES Employes(Empno),
    FOREIGN key id_attributeur REFERENCES Employes(Empno),
    FOREIGN key id_department REFERENCES Departements(deptno)
);