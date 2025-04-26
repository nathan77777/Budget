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


