; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CAccessDiasDlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "AccessDias.h"

ClassCount=8
Class1=CAccessDiasApp
Class2=CAccessDiasDlg

ResourceCount=9
Resource2=IDD_ALLERA
Resource3=IDD_CRITERETRI
Resource4=IDD_RAPPORT
Resource1=IDR_MAINFRAME
Class3=CDlgAllerA
Resource5=IDD_GLG_RENOMMER_IMAGE
Class4=CDlgRecherche
Class5=CDlgRapport
Resource6=IDD_ACCESSDIAS_DIALOG
Class6=CDlgCritereTri
Resource7=IDD_RECHERCHE
Class7=CNewJpegSerie
Resource8=IDD_NEW_JPEG_SERIE
Class8=CDlgRenommerImage
Resource9=IDR_MENUDIAS

[CLS:CAccessDiasApp]
Type=0
HeaderFile=AccessDias.h
ImplementationFile=AccessDias.cpp
Filter=N
VirtualFilter=AC
LastObject=ID_MANIPULATION_INSERER

[CLS:CAccessDiasDlg]
Type=0
HeaderFile=Accesdlg.h
ImplementationFile=Accesdlg.cpp
Filter=D
VirtualFilter=dWC
LastObject=ID_OUTILS_COMPLETE_ENTREES_JPEGS
BaseClass=CDialog


[DLG:IDD_ACCESSDIAS_DIALOG]
Type=1
Class=CAccessDiasDlg
ControlCount=36
Control1=IDC_STATIC,button,1342177287
Control2=IDC_STATIC,static,1342308352
Control3=IDC_SUJET,edit,1350631552
Control4=IDC_STATIC,static,1342308352
Control5=IDC_DATE,edit,1350631552
Control6=IDC_STATIC,static,1342308352
Control7=IDC_BOITE,edit,1350631552
Control8=IDC_STATIC,static,1342308352
Control9=IDC_RANGEE,edit,1350631552
Control10=IDC_STATIC,static,1342308352
Control11=IDC_NUMERO,edit,1350631552
Control12=IDC_CAMERADIGITALE,button,1342242819
Control13=IDC_STATIC,static,1342308352
Control14=IDC_PREMIERNIVEAU,edit,1350631552
Control15=IDC_STATIC,static,1342308352
Control16=IDC_SECONDNIVEAU,edit,1350631552
Control17=IDC_STATIC,static,1342308352
Control18=IDC_TROISIEMENIVEAU,edit,1350631552
Control19=IDC_STATIC,static,1342308352
Control20=IDC_SUJETDIAS,edit,1352728644
Control21=IDC_AGRANDI,button,1342242819
Control22=IDC_CLASSE,button,1342242819
Control23=IDC_VERIFIE,button,1342242819
Control24=IDC_STATIC,static,1342308352
Control25=IDC_COMMENTAIRE,edit,1352728644
Control26=IDC_STATIC,static,1342308352
Control27=IDC_NOFICHE,static,1342308352
Control28=IDC_STATIC,static,1342308352
Control29=IDC_TOTAL,static,1342308352
Control30=ID_DPLACEMENTS_RECULER,button,1342242816
Control31=ID_DPLACEMENTS_AVANCER,button,1342242816
Control32=ID_DPLACEMENTS_DBUT,button,1342242816
Control33=ID_DPLACEMENTS_FIN,button,1342242816
Control34=IDC_NOMFICHIER,edit,1484849280
Control35=IDC_STATIC,static,1342308352
Control36=ID_RENOMMER_FICHIER,button,1342242816

[MNU:IDR_MENUDIAS]
Type=1
Class=CAccessDiasDlg
Command1=ID_FICHIER_CHARGER
Command2=ID_FICHIER_SAUVER
Command3=ID_FICHIER_IMPORTEFICHIERTEXTE
Command4=ID_FICHIER_FUSIONNER
Command5=ID_FICHIER_QUITTER
Command6=ID_DPLACEMENTS_RECULER
Command7=ID_DPLACEMENTS_AVANCER
Command8=ID_DPLACEMENTS_DBUT
Command9=ID_DPLACEMENTS_FIN
Command10=ID_DPLACEMENTS_ALLER
Command11=ID_MANIPULATION_INSERER
Command12=ID_MANIPULATION_EFFACE
Command13=ID_EFFACE_FICHE_VIDES
Command14=ID_EFFACE_CRITERE
Command15=ID_MANIPULATION_RECHERCHE
Command16=ID_MANIPULATION_TRIER
Command17=ID_MANIPULATION_REPORTELECONTENU
Command18=ID_MANIPULATION_RAPPORT
Command19=ID_OUTILS_PREPARE_ENTREES_JPEGS
Command20=ID_OUTILS_GENERE_JPEGS
Command21=ID_OUTILS_CREE_COMMENT_HTML
Command22=ID_OUTILS_RECREE_TOUT_LES_COMMENTAIRES
Command23=ID_OUTILS_COMPLETE_ENTREES_JPEGS
CommandCount=23

[DLG:IDD_ALLERA]
Type=1
Class=CDlgAllerA
ControlCount=4
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_STATIC,button,1342177287
Control4=IDC_NOFICHE,edit,1350631552

[CLS:CDlgAllerA]
Type=0
HeaderFile=dlgallera.h
ImplementationFile=dlgallera.cpp
Filter=D
VirtualFilter=dWC
LastObject=CDlgAllerA

[DLG:IDD_RECHERCHE]
Type=1
Class=CDlgRecherche
ControlCount=12
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_STATIC,button,1342177287
Control4=IDC_LISTECHAMPS1,combobox,1344339971
Control5=IDC_STATIC,static,1342308352
Control6=IDC_VALEUR1,edit,1350631560
Control7=IDC_LISTECHAMPS2,combobox,1344339971
Control8=IDC_STATIC,static,1342308352
Control9=IDC_VALEUR2,edit,1350631560
Control10=IDC_LISTECHAMPS3,combobox,1344339971
Control11=IDC_STATIC,static,1342308352
Control12=IDC_VALEUR3,edit,1350631560

[CLS:CDlgRecherche]
Type=0
HeaderFile=dlgrecherche.h
ImplementationFile=dlgrecherche.cpp
Filter=D
VirtualFilter=dWC
LastObject=IDC_LISTECHAMPS1

[DLG:IDD_RAPPORT]
Type=1
Class=CDlgRapport
ControlCount=16
Control1=IDC_STATIC,button,1342177287
Control2=IDC_LISTECHAMPS1,combobox,1344339971
Control3=IDC_STATIC,static,1342308352
Control4=IDC_VALEUR1,edit,1350631560
Control5=IDC_LISTECHAMPS2,combobox,1344339971
Control6=IDC_STATIC,static,1342308352
Control7=IDC_VALEUR2,edit,1350631560
Control8=IDC_LISTECHAMPS3,combobox,1344339971
Control9=IDC_STATIC,static,1342308352
Control10=IDC_VALEUR3,edit,1350631560
Control11=IDC_STATIC,button,1342177287
Control12=IDC_RAPPORT,button,1342177289
Control13=IDC_ETIQUETTES,button,1342177289
Control14=IDC_COUNT,button,1342177289
Control15=IDOK,button,1342242817
Control16=IDCANCEL,button,1342242816

[CLS:CDlgRapport]
Type=0
HeaderFile=dlgrapport.h
ImplementationFile=dlgrapport.cpp
Filter=D
VirtualFilter=dWC
LastObject=CDlgRapport

[DLG:IDD_CRITERETRI]
Type=1
Class=CDlgCritereTri
ControlCount=4
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_STATIC,button,1342177287
Control4=IDC_CRITERETRI,combobox,1344339971

[CLS:CDlgCritereTri]
Type=0
HeaderFile=DlgCritereTri.h
ImplementationFile=DlgCritereTri.cpp
BaseClass=CDialog
Filter=D
VirtualFilter=dWC
LastObject=CDlgCritereTri

[DLG:IDD_NEW_JPEG_SERIE]
Type=1
Class=CNewJpegSerie
ControlCount=8
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_STATIC,static,1342308352
Control4=IDC_SUJET,edit,1350631552
Control5=IDC_STATIC,static,1342308352
Control6=IDC_DATE,edit,1350631552
Control7=IDC_STATIC,static,1342308352
Control8=IDC_COMMENTAIRE,edit,1352728644

[CLS:CNewJpegSerie]
Type=0
HeaderFile=NewJpegSerie.h
ImplementationFile=NewJpegSerie.cpp
BaseClass=CDialog
Filter=D
VirtualFilter=dWC
LastObject=CNewJpegSerie

[DLG:IDD_GLG_RENOMMER_IMAGE]
Type=1
Class=CDlgRenommerImage
ControlCount=4
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_EDIT1,edit,1350631552
Control4=IDC_STATIC,static,1342308352

[CLS:CDlgRenommerImage]
Type=0
HeaderFile=DlgRenommerImage.h
ImplementationFile=DlgRenommerImage.cpp
BaseClass=CDialog
Filter=D
VirtualFilter=dWC
LastObject=CDlgRenommerImage

