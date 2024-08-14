// Accesdlg.cpp : implementation file
//

#include "stdafx.h"
#include "AccessDias.h"
#include "FicheDias.h"
#include "Accesdlg.h"
#include "dlgallera.h"
#include "dlgrecherche.h"
#include "dlgrapport.h"
#include "DlgCritereTri.h"
#include "NewJpegSerie.h"
#include <io.h>
#include <process.h>
#include <direct.h>
#include "DlgRenommerImage.h"
#include "strsafe.h"
#include "DlgUpdateComment.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

//Remove all space from a box number
char *RemoveSpaces(const char *pszBoxNumberString,char *pszDest,size_t p_nDestSize)
{
	int nLen=strlen(pszBoxNumberString);
	char szTmp[2];
	int nCompt;
	
	*pszDest=0;
	szTmp[1]=0;

	//Remove spaces
	for (nCompt=0;nCompt<nLen;nCompt++)
	{
		if (!isspace(pszBoxNumberString[nCompt]))
		{
			szTmp[0]=pszBoxNumberString[nCompt];
			StringCchCat(pszDest,p_nDestSize,szTmp);
		}
	}
	char szNoSpace[20];
	StringCchCopy(szNoSpace,sizeof(szNoSpace),pszDest);
	nLen=strlen(szNoSpace);
	*pszDest=0;
	
	//Format digits
	for (nCompt=0;nCompt<nLen;nCompt++)
	{
		if (!isdigit(szNoSpace[nCompt]))
		{
			szTmp[0]=szNoSpace[nCompt];
			StringCchCat(pszDest,p_nDestSize,szTmp);
		}
		else
		{
			//We suppose the rest of the string is a number
			_snprintf_s(pszDest+strlen(pszDest),p_nDestSize-strlen(pszDest),p_nDestSize-strlen(pszDest),"%03d",atoi(szNoSpace+nCompt));
			break;
		}
	}

	return pszDest;
}


/////////////////////////////////////////////////////////////////////////////
// CAccessDiasDlg dialog

CAccessDiasDlg::CAccessDiasDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CAccessDiasDlg::IDD, pParent)
{
	m_nNoFiche=0;
	m_bTakeLast=1;
	m_bSauve=0;
	m_Banque.CreeFiche();

	//{{AFX_DATA_INIT(CAccessDiasDlg)
	m_Sujet = _T("");
	m_Date = _T("01/01/1995");
	m_Boite = _T("v1");
	m_nRangee = 1;
	m_nNumero = 1;
	m_SujetDias = _T("");
	m_bAgrandi = FALSE;
	m_bClasse = FALSE;
	m_bVerifie = FALSE;
	m_Commentaire = _T("");
	m_bCameraDigitale = FALSE;
	m_PremierNiveau = _T("");
	m_SecondNiveau = _T("");
	m_TroisiemeNiveau = _T("");
	m_NomFichierJpeg = _T("");
	m_Total = _T("1");
	m_NoFiche = _T("1");
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CAccessDiasDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAccessDiasDlg)
	DDX_Text(pDX, IDC_SUJET, m_Sujet);
	DDX_Text(pDX, IDC_DATE, m_Date);
	DDV_MaxChars(pDX, m_Date, 30);
	DDX_Text(pDX, IDC_BOITE, m_Boite);
	DDV_MaxChars(pDX, m_Boite, 3);
	DDX_Text(pDX, IDC_RANGEE, m_nRangee);
	DDV_MinMaxUInt(pDX, m_nRangee, 0, 6);
	DDX_Text(pDX, IDC_NUMERO, m_nNumero);
	DDX_Text(pDX, IDC_SUJETDIAS, m_SujetDias);
	DDX_Check(pDX, IDC_AGRANDI, m_bAgrandi);
	DDX_Check(pDX, IDC_CLASSE, m_bClasse);
	DDX_Check(pDX, IDC_VERIFIE, m_bVerifie);
	DDX_Text(pDX, IDC_COMMENTAIRE, m_Commentaire);
	DDX_Text(pDX, IDC_TOTAL, m_Total);
	DDX_Text(pDX, IDC_NOFICHE, m_NoFiche);
	DDX_Check(pDX, IDC_CAMERADIGITALE, m_bCameraDigitale);
	DDX_Text(pDX, IDC_PREMIERNIVEAU, m_PremierNiveau);
	DDX_Text(pDX, IDC_SECONDNIVEAU, m_SecondNiveau);
	DDX_Text(pDX, IDC_TROISIEMENIVEAU, m_TroisiemeNiveau);
	DDX_Text(pDX, IDC_NOMFICHIER, m_NomFichierJpeg);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAccessDiasDlg, CDialog)
	//{{AFX_MSG_MAP(CAccessDiasDlg)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(ID_DPLACEMENTS_AVANCER, OnDeplacementsAvancer)
	ON_BN_CLICKED(ID_DPLACEMENTS_DBUT, OnDeplacementsDebut)
	ON_BN_CLICKED(ID_DPLACEMENTS_FIN, OnDeplacementsFin)
	ON_BN_CLICKED(ID_DPLACEMENTS_RECULER, OnDeplacementsReculer)
	ON_COMMAND(ID_FICHIER_CHARGER, OnFichierCharger)
	ON_COMMAND(ID_FICHIER_SAUVER, OnFichierSauver)
	ON_COMMAND(ID_FICHIER_QUITTER, OnFichierQuitter)
	ON_COMMAND(ID_DPLACEMENTS_ALLER, OnDeplacementsAller)
	ON_COMMAND(ID_MANIPULATION_EFFACE, OnManipulationEfface)
	ON_COMMAND(ID_MANIPULATION_REPORTELECONTENU, OnManipulationReportelecontenu)
	ON_COMMAND(ID_MANIPULATION_RECHERCHE, OnManipulationRecherche)
	ON_COMMAND(ID_MANIPULATION_RAPPORT, OnManipulationRapport)
	ON_COMMAND(ID_MANIPULATION_INSERER, OnManipulationInserer)
	ON_COMMAND(ID_MANIPULATION_TRIER, OnManipulationTrier)
	ON_COMMAND(ID_FICHIER_IMPORTEFICHIERTEXTE, OnFichierImporteFichierTexte)
	ON_COMMAND(ID_EFFACE_FICHE_VIDES, OnEffaceFicheVides)
	ON_COMMAND(ID_FICHIER_FUSIONNER, OnFichierFusionner)
	ON_COMMAND(ID_EFFACE_CRITERE, OnEffaceCritere)
	ON_COMMAND(ID_OUTILS_PREPARE_ENTREES_JPEGS, OnOutilsPrepareEntreesJpegs)
	ON_COMMAND(ID_OUTILS_GENERE_JPEGS, OnOutilsGenereJpegs)
	ON_COMMAND(ID_OUTILS_CREE_COMMENT_HTML, OnOutilsCreeCommentHtml)
	ON_COMMAND(ID_OUTILS_RECREE_TOUT_LES_COMMENTAIRES, OnOutilsRecreeToutLesCommentaires)
	ON_BN_CLICKED(ID_RENOMMER_FICHIER, OnRenommerFichier)
	ON_COMMAND(ID_OUTILS_COMPLETE_ENTREES_JPEGS, OnOutilsCompleteEntreesJpegs)
	//}}AFX_MSG_MAP
	ON_COMMAND(ID_FICHIER_REPERTOIREDIAS, &CAccessDiasDlg::OnFichierRepertoiredias)
	ON_COMMAND(ID_MANIPULATION_METAJOUR_COMMENTAIRE, &CAccessDiasDlg::OnManipulationMetajourCommentaire)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAccessDiasDlg message handlers

BOOL CAccessDiasDlg::OnInitDialog()
{
	CDialog::OnInitDialog();
	CenterWindow();

	// TODO: Add extra initialization here
	UpdateBoutons();
	GetDlgItem(IDC_SUJET)->SetFocus();
	
	return 0;  // return TRUE  unless you set the focus to a control
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CAccessDiasDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

// The system calls this to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CAccessDiasDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}


void CAccessDiasDlg::UpdateBoutons()
{
int bActif=1;
UINT nEnable=MF_BYCOMMAND|MF_ENABLED;
CMenu *pMenu=GetMenu();
int l_nTailleBanque=m_Banque.GetTaille();

	/*Aller à*/
	if (l_nTailleBanque<=1)
		nEnable=MF_BYCOMMAND|MF_GRAYED;
	pMenu->EnableMenuItem(ID_DPLACEMENTS_ALLER,nEnable);

	/*Début*/
	if(!m_nNoFiche || !l_nTailleBanque) {
		bActif=0;
		nEnable=MF_BYCOMMAND|MF_GRAYED;
	}
	else {
		bActif=1;
		nEnable=MF_BYCOMMAND|MF_ENABLED;
	}
	GetDlgItem(ID_DPLACEMENTS_DBUT)->EnableWindow(bActif);
	pMenu->EnableMenuItem(ID_DPLACEMENTS_DBUT,nEnable);

	/*Fin*/
	if(m_nNoFiche==l_nTailleBanque-1 || !l_nTailleBanque) {
		bActif=0;
		nEnable=MF_BYCOMMAND|MF_GRAYED;
	}
	else {
		bActif=1;
		nEnable=MF_BYCOMMAND|MF_ENABLED;
	}
	GetDlgItem(ID_DPLACEMENTS_FIN)->EnableWindow(bActif);
	pMenu->EnableMenuItem(ID_DPLACEMENTS_FIN,nEnable);

	/*Reculer*/
	if(m_nNoFiche || !l_nTailleBanque) {
		bActif=1;
		nEnable=MF_BYCOMMAND|MF_ENABLED;
	}
	else {
		bActif=0;
		nEnable=MF_BYCOMMAND|MF_GRAYED;
	}
	GetDlgItem(ID_DPLACEMENTS_RECULER)->EnableWindow(bActif);
	pMenu->EnableMenuItem(ID_DPLACEMENTS_RECULER,nEnable);

	/*Effacer*/
	if(l_nTailleBanque>1)
		nEnable=MF_BYCOMMAND|MF_ENABLED;
	else
		nEnable=MF_BYCOMMAND|MF_GRAYED;
	pMenu->EnableMenuItem(ID_MANIPULATION_EFFACE,nEnable);

	MetAJourControles();	/*Met à jour la fiche*/
}

void CAccessDiasDlg::MetAJourControles()
{
	int l_nTailleBanque=m_Banque.GetTaille();
	if (l_nTailleBanque) {
		CFicheDias &Dia=m_Banque.m_Dias[m_nNoFiche];

		m_Sujet=Dia.m_Sujet;
		m_Date=Dia.m_Date;
		if (Dia.m_bCameraDigitale)
		{
			m_PremierNiveau=Dia.m_PremierNiveau;
			m_SecondNiveau=Dia.m_SecondNiveau;
			m_TroisiemeNiveau=Dia.m_TroisiemeNiveau;
			m_Boite="";
			m_nRangee=0;
		}
		else
		{
			m_PremierNiveau=m_SecondNiveau=m_TroisiemeNiveau="";
			m_Boite=Dia.m_Boite;
			m_nRangee=Dia.m_nRangee;
		}
		m_nNumero=Dia.m_nNumero;
		m_SujetDias=Dia.m_SujetDias;
		m_bAgrandi=Dia.m_bAgrandi;
		m_bClasse=Dia.m_bClasse;
		m_bVerifie=Dia.m_bVerifie;
		m_Commentaire=Dia.m_Commentaire;
		m_bCameraDigitale=Dia.m_bCameraDigitale;
		m_NoFiche.Format("%d",m_nNoFiche+1);
		m_Total.Format("%d",l_nTailleBanque);
		m_NomFichierJpeg=Dia.m_NomFichierJpeg;

		UpdateData(FALSE);
	}
}

CString & CAccessDiasDlg::NettoieTexte(CString &Texte)
{
	Texte.TrimLeft();
	Texte.TrimRight();
	return(Texte);
}

void CAccessDiasDlg::RecupereControles()
{
	if (m_Banque.GetTaille()) {
		CFicheDias &Dia=m_Banque.m_Dias[m_nNoFiche];

		Dia.m_Sujet=NettoieTexte(m_Sujet);
		Dia.m_Date=NettoieTexte(m_Date);

		if (m_bCameraDigitale)
		{
			Dia.m_PremierNiveau=NettoieTexte(m_PremierNiveau);
			Dia.m_SecondNiveau=NettoieTexte(m_SecondNiveau);
			Dia.m_TroisiemeNiveau=NettoieTexte(m_TroisiemeNiveau);
			Dia.m_Boite="";
			Dia.m_nRangee=0;
		}
		else
		{
			Dia.m_PremierNiveau=Dia.m_SecondNiveau=m_TroisiemeNiveau="";
			Dia.m_Boite=NettoieTexte(m_Boite);
			Dia.m_nRangee=m_nRangee;
		}
		
		Dia.m_nNumero=m_nNumero;
		Dia.m_SujetDias=NettoieTexte(m_SujetDias);
		Dia.m_bAgrandi=m_bAgrandi;
		Dia.m_bClasse=m_bClasse;
		Dia.m_bVerifie=m_bVerifie;
		Dia.m_Commentaire=NettoieTexte(m_Commentaire);
		Dia.m_bCameraDigitale=m_bCameraDigitale;
		Dia.m_NomFichierJpeg=m_NomFichierJpeg;
		m_bSauve=0;
	}
}

void CAccessDiasDlg::OnDeplacementsAvancer() 
{
	// TODO: Add your control notification handler code here
	if (!UpdateData())
		return;
	
	if (m_nNoFiche<m_Banque.GetTaille()-1)
		m_nNoFiche++;
	else {
		m_nNoFiche++;
		m_Banque.CreeFiche(m_bTakeLast);
	}
	UpdateBoutons();
}

void CAccessDiasDlg::OnDeplacementsDebut() 
{
	// TODO: Add your control notification handler code here
	if (!UpdateData())
		return;

	m_nNoFiche=0;
	UpdateBoutons();
}

void CAccessDiasDlg::OnDeplacementsFin() 
{
	// TODO: Add your control notification handler code here
	if (!UpdateData())
		return;

	m_nNoFiche=m_Banque.GetTaille()-1;
	UpdateBoutons();
}

void CAccessDiasDlg::OnDeplacementsReculer() 
{
	// TODO: Add your control notification handler code here
	if (!UpdateData())
		return;

	m_nNoFiche--;
	UpdateBoutons();
}

void CAccessDiasDlg::OnDeplacementsAller() 
{
	// TODO: Add your command handler code here
	if (!UpdateData())
		return;

	CDlgAllerA Dlg(this,m_nNoFiche,m_Banque.GetTaille());
	if (Dlg.DoModal()==IDOK) {
		m_nNoFiche=Dlg.m_nNoFiche-1;
		UpdateBoutons();
	}
}

void CAccessDiasDlg::OnFichierCharger() 
{
	if (!m_bSauve) {
		int bBanqueVide=0;

		/*Vérifie si c'est la banque vide de démarrage*/
		if (m_Banque.GetTaille()==1) {
			if (UpdateData()) {
				CFicheDias Dia;

				if (Dia==m_Banque.m_Dias[0])
					bBanqueVide=1;
			}
		}

		if (!bBanqueVide)
			if (MessageBox("Voulez-vous sauver ?","Dias",MB_YESNO|MB_ICONQUESTION)==IDYES)
				OnFichierSauver();
	}

	/*Récupère le nom du dernier fichier chargé*/
	std::string szNom=GetRegistryValue("NomFichier");

	CFileDialog Dlg(1, "bdd", !szNom.empty() ? szNom.c_str():NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT,
		"Données dias|*.bdd||",this);

	if (Dlg.DoModal()==IDCANCEL)
		return;

	m_nNoFiche=0;
	if (!m_Banque.LitBanque(Dlg.GetPathName())) {
		m_Banque.CreeFiche();	/*Met une fiche vide*/
		MessageBox("Erreur lors du chargement");
		m_NomFichier.Empty();
	}
	else {
		m_NomFichier=Dlg.GetPathName();

		/*Sauve le nom*/
		SaveRegistryValue("NomFichier",(LPCTSTR)m_NomFichier);
	}
	
	UpdateBoutons();
	m_bSauve=0;
}

void CAccessDiasDlg::OnFichierSauver() 
{
CString Chemin;

	if (!UpdateData())
		return;

	if (!m_NomFichier.GetLength()) {
		CFileDialog Dlg(0, "bdd", NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT,
				"Données dias|*.bdd||",this);

		if (Dlg.DoModal()==IDCANCEL)
			return;
		Chemin=Dlg.GetPathName();
	}
	else
		Chemin=m_NomFichier;

	if (!m_Banque.SauveBanque(Chemin))
		MessageBox("Erreur de la sauvegarde");
	else
		m_bSauve=1;
}

void CAccessDiasDlg::OnFichierQuitter() 
{
	// TODO: Add your command handler code here
	if (!m_bSauve) {
		if (MessageBox("Voulez-vous sauver ?","Dias",MB_YESNO|MB_ICONQUESTION)==IDYES)
			OnFichierSauver();
	}
	EndDialog(IDOK);	
}


BOOL CAccessDiasDlg::UpdateData( BOOL bSaveAndValidate)
{
BOOL bRet=CDialog::UpdateData(bSaveAndValidate);

	if (bSaveAndValidate) {	/*Mode récupération*/
		if (bRet)
			RecupereControles();
	}
	return(bRet);
}

void CAccessDiasDlg::OnManipulationEfface() 
{
	// TODO: Add your command handler code here
	if (MessageBox("Etes-vous sur de supprimer cette fiche ?","Dias",MB_YESNO|MB_ICONQUESTION)==IDNO)
		return;

	int l_nTailleBanque=m_Banque.GetTaille();
	m_Banque.m_Dias.RemoveAt(m_nNoFiche);
	if (m_nNoFiche>=l_nTailleBanque)
		m_nNoFiche=l_nTailleBanque-1;

	UpdateBoutons();
	m_bSauve=0;
}

void CAccessDiasDlg::OnManipulationReportelecontenu() 
{
	m_bTakeLast=!m_bTakeLast;

	GetMenu()->CheckMenuItem(ID_MANIPULATION_REPORTELECONTENU,
				MF_BYCOMMAND|(m_bTakeLast ? MF_CHECKED:MF_UNCHECKED));
}

void CAccessDiasDlg::OnCancel() 
{
	// TODO: Add extra cleanup here
	OnFichierQuitter();	
}


void CAccessDiasDlg::OnManipulationRecherche() 
{
	// TODO: Add your command handler code here
	if (!UpdateData())
		return;

	CDlgRecherche Dlg(this);	

	if (Dlg.DoModal()==IDCANCEL)
		return;

	if (!Dlg.m_ValChamp[0].GetLength() && !Dlg.m_ValChamp[1].GetLength()
		 && !Dlg.m_ValChamp[2].GetLength()) {
		MessageBox("Critère invalide");
		return;
	}

	/*Fait la recherche*/
	int nCompt;
	int l_nTailleBanque=m_Banque.GetTaille();
	for (nCompt=m_nNoFiche;nCompt<l_nTailleBanque;nCompt++) {
		/*Trouvé*/
		if (m_Banque.CorrespondsCritere(nCompt,Dlg.m_ValChamp,Dlg.m_nChamp)) {
			m_nNoFiche=nCompt;
			UpdateBoutons();
			break;
		}
	}

	if (nCompt==l_nTailleBanque)
		MessageBox("Aucune dias n'a été trouvée");
}


void CAccessDiasDlg::OnManipulationRapport() 
{
	// TODO: Add your command handler code here
	if (!UpdateData())
		return;

	CDlgRapport Dlg(this);	

	if (Dlg.DoModal()==IDCANCEL)
		return;

	if (!Dlg.m_ValChamp[0].GetLength() && !Dlg.m_ValChamp[1].GetLength()
		 && !Dlg.m_ValChamp[2].GetLength()) {
		MessageBox("Critère invalide");
		return;
	}

	if (Dlg.m_bEtiquettes || Dlg.m_bRapport) {
		HDC hDC=0;
		CPrintDialog PrintDlg(0,PD_USEDEVMODECOPIES | PD_HIDEPRINTTOFILE | PD_NOSELECTION, this);

		if (PrintDlg.DoModal()==IDOK) {
			hDC=PrintDlg.GetPrinterDC();
			if (Dlg.m_bRapport)
				ImprimeRapport(hDC,Dlg.m_ValChamp,Dlg.m_nChamp);
			else
				ImprimeEtiquettes(hDC,Dlg.m_ValChamp,Dlg.m_nChamp);
		}
	}
	else {
		int nCompt,nTrouve=0;
		CString Texte;

		/*Fait la recherche*/
		int l_nTailleBanque=m_Banque.GetTaille();
		for (nCompt=m_nNoFiche;nCompt<l_nTailleBanque;nCompt++) {
			/*Trouvé une fiche*/
			if (m_Banque.CorrespondsCritere(nCompt,Dlg.m_ValChamp,Dlg.m_nChamp))
				nTrouve++;
		}
		Texte.Format("Trouvé %d occurences",nTrouve);
		MessageBox(Texte,"Dias");
	}
}

void CAccessDiasDlg::ImprimeRapport(HDC hDC,CString *pValChamp,int nChamp[3])
{
int nCompt;
int bFirst=1;
CDC *pDC=CDC::FromHandle(hDC);
DOCINFO DocInfo={sizeof(DOCINFO),"Rapport dias",NULL};
/*Se renseigne sur l'imprimante*/
CSize SizePix(pDC->GetDeviceCaps(HORZRES),pDC->GetDeviceCaps(VERTRES));
CSize SizeLog;
int nLignes,nCurLine,nCurPage=1;
int bNeedEndDoc=0;
CFont Police,*pOldFont;
TEXTMETRIC tm;
CSize TailleRangee,TailleNum;
CString Texte;
	
	Police.CreateFont(20*11,0,0, 0, 400, 0, 0, 0,
				ANSI_CHARSET,OUT_DEFAULT_PRECIS,
				CLIP_DEFAULT_PRECIS,DEFAULT_QUALITY,
				DEFAULT_PITCH|FF_DONTCARE,
				"Times New Roman");

	/*Fait la recherche*/
	int l_nTailleBanque=m_Banque.GetTaille();
	for (nCompt=m_nNoFiche;nCompt<l_nTailleBanque;nCompt++) {
		/*Trouvé une fiche*/
		if (m_Banque.CorrespondsCritere(nCompt,pValChamp,nChamp)) {
			CFicheDias &Dia=m_Banque.m_Dias[nCompt];

			if (bFirst) {
				/*Initie l'impression*/
				pDC->StartDoc(&DocInfo);
				pDC->StartPage();
				bNeedEndDoc=1;
				
				/*Prépare le DC*/
				pDC->SetMapMode(MM_TWIPS);	/*1/20 de point*/
				pOldFont=pDC->SelectObject(&Police);
				pDC->SetTextAlign(TA_LEFT|TA_BASELINE);
				
				/*Récupère les infos*/
				pDC->GetTextMetrics(&tm);
				SizeLog=SizePix;
				pDC->DPtoLP(&SizeLog);
				nLignes=SizeLog.cy/tm.tmHeight;

				/*Infos texte*/
				nCurLine=1;

				/*Affiche l'entête*/
				Texte.Format("Boîte numéro: %s",(LPCTSTR)Dia.m_Boite);
				pDC->TextOut(0,-nCurLine++*tm.tmHeight,Texte);
				Texte.Format("Sujet du film: %s",(LPCTSTR)Dia.m_Sujet);
				pDC->TextOut(0,-nCurLine++*tm.tmHeight,Texte);
				Texte.Format("Date: %s",(LPCTSTR)Dia.m_Date);
				pDC->TextOut(0,-nCurLine++*tm.tmHeight,Texte);
				nCurLine++;
				TailleRangee=pDC->GetTextExtent("Rangée    ",10);
				TailleNum=pDC->GetTextExtent("Numéro    ",10);

				/*Entête*/
				Texte.Format("Rangée    Numéro    Sujet de la dia");
				pDC->TextOut(0,-nCurLine++*tm.tmHeight,Texte);
				nCurLine++;
				bFirst=0;
			}

			/*Passer à la page ?*/
			if (!(nLignes-3>=nCurLine)) {
				nCurLine++;
				Texte.Format("Page n° %d",nCurPage++);
				pDC->TextOut(TailleRangee.cx*4,-nCurLine*tm.tmHeight,Texte);
				
				pDC->SelectObject(pOldFont);
				pDC->EndPage();
				pDC->StartPage();
				
				/*Prépare le DC*/
				pDC->SetMapMode(MM_TWIPS);	/*1/20 de point*/
				pOldFont=pDC->SelectObject(&Police);
				pDC->SetTextAlign(TA_LEFT|TA_BASELINE);

				/*Entête*/
				nCurLine=1;
				Texte.Format("Rangée    Numéro    Sujet de la dia");
				pDC->TextOut(0,-nCurLine++*tm.tmHeight,Texte);
				nCurLine++;
			}
			
			/*Met la dia*/
			Texte.Format("%-10d",Dia.m_nRangee);
			pDC->TextOut(0,-nCurLine*tm.tmHeight,Texte);
			Texte.Format("%-10d",Dia.m_nNumero);
			pDC->TextOut(TailleRangee.cx,-nCurLine*tm.tmHeight,Texte);
			pDC->TextOut(TailleRangee.cx+TailleNum.cx,-nCurLine++*tm.tmHeight,Dia.m_SujetDias);
		}
	}
	
	if (bNeedEndDoc) {
		nCurLine=nLignes-1;
		Texte.Format("Page n° %d",nCurPage);
		pDC->TextOut(TailleRangee.cx*4,-nCurLine*tm.tmHeight,Texte);
		
		pDC->SelectObject(pOldFont);
		pDC->EndPage();

		pDC->EndDoc();
	}
}

void CAccessDiasDlg::ImprimeEtiquettes(HDC hDC,CString *pValChamp,int nChamp[3])
{
int nCompt;
int bFirst=1;
CDC *pDC=CDC::FromHandle(hDC);
DOCINFO DocInfo={sizeof(DOCINFO),"Etiquettes dias",NULL};
/*Se renseigne sur l'imprimante*/
CSize SizePix(pDC->GetDeviceCaps(HORZRES),pDC->GetDeviceCaps(VERTRES));
CSize SizeLog;
int bNeedEndDoc=0;
CFont Police,*pOldFont;
TEXTMETRIC tm;
CSize TailleEtiqu;
CString Texte;
int nLigneEtiqu,nColEtiqu;
int nMaxLignesParEtiqu,nMaxColsParEtiqu;
int nColDia,nLigneDia;
	
	Police.CreateFont(20*10,0,0, 0, 400, 0, 0, 0,
				ANSI_CHARSET,OUT_DEFAULT_PRECIS,
				CLIP_DEFAULT_PRECIS,DEFAULT_QUALITY,
				DEFAULT_PITCH|FF_DONTCARE,
				"Times New Roman");

	/*Fait la recherche*/
	int l_nTailleBanque=m_Banque.GetTaille();
	for (nCompt=m_nNoFiche;nCompt<l_nTailleBanque;nCompt++) {
		/*Trouvé une fiche*/
		if (m_Banque.CorrespondsCritere(nCompt,pValChamp,nChamp)) {
			CFicheDias &Dia=m_Banque.m_Dias[nCompt];

			if (bFirst) {
				/*Initie l'impression*/
				pDC->StartDoc(&DocInfo);
				pDC->StartPage();
				bNeedEndDoc=1;

				/*Taille papier: longueur= 16838, largeur= 11906
				taille étiquette:  longueur=  4209, largeur=  5953*/
				
				/*Prépare le DC*/
				pDC->SetMapMode(MM_TWIPS);	/*1/20 de point*/
				pOldFont=pDC->SelectObject(&Police);
				pDC->SetTextAlign(TA_LEFT|TA_TOP);
				
				/*Récupère les infos*/
				pDC->GetTextMetrics(&tm);
				SizeLog=SizePix;
				pDC->DPtoLP(&SizeLog);

				/*Infos texte*/
				nColEtiqu=nLigneEtiqu=0;
				nColDia=0;
				nLigneDia=1;

				/*Taille*/
				TailleEtiqu=pDC->GetTextExtent("B v10 R 1 N 50",14);
				TailleEtiqu.cx=(TailleEtiqu.cx*10)/9;
				TailleEtiqu.cy=(TailleEtiqu.cy*10)/9;
				nMaxLignesParEtiqu=4209/TailleEtiqu.cy;
				nMaxColsParEtiqu=5953/TailleEtiqu.cx;

				bFirst=0;
			}

			/*Position de la dias*/
			if (nColDia>=nMaxColsParEtiqu) {
				/*Passe à la ligne*/
				nColDia=0;
				nLigneDia++;

				/*Change d'étiquette*/
				if (nLigneDia>=nMaxLignesParEtiqu-1) {		/*Evite de coller à la limite*/
					nLigneDia=1;	/*Idem*/
					nColEtiqu++;
					
					/*Change de ligne d'étiquette*/
					if (nColEtiqu>=2) {
						nColEtiqu=0;
						nLigneEtiqu++;

						/*Change de page*/
						if (nLigneEtiqu>=4) {
							nLigneEtiqu=0;

							pDC->SelectObject(pOldFont);
							pDC->EndPage();
							pDC->StartPage();
				
							/*Prépare le DC*/
							pDC->SetMapMode(MM_TWIPS);	/*1/20 de point*/
							pOldFont=pDC->SelectObject(&Police);
							pDC->SetTextAlign(TA_LEFT|TA_TOP);
						}
					}
				}

			}
			
			/*Met la dia*/
			Texte.Format("B %3s R %d N %2d",(LPCTSTR)Dia.m_Boite,
									Dia.m_nRangee,Dia.m_nNumero);
			pDC->TextOut(nColEtiqu*5953+nColDia*TailleEtiqu.cx,
				-(nLigneEtiqu*4209+nLigneDia*TailleEtiqu.cy),Texte);
			nColDia++;
		}
	}
	
	if (bNeedEndDoc) {
		pDC->SelectObject(pOldFont);
		pDC->EndPage();

		pDC->EndDoc();
	}
}


void CAccessDiasDlg::OnManipulationInserer() 
{
	// TODO: Add your control notification handler code here
	if (!UpdateData())
		return;
	
	if (!m_Banque.GetTaille()) {
		m_Banque.CreeFiche(0);
		m_nNoFiche=0;
	}
	else {
		if (m_Banque.InsereFiche(m_nNoFiche,m_bTakeLast))
			m_nNoFiche++;
		else
			MessageBox("Impossible d'insérer: pas assez de mémoire","Dias",
						MB_ICONHAND|MB_OK);
	}
	UpdateBoutons();
}

int TriSujet(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_Sujet,pF2->m_Sujet));
}

int TriDate(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_Date,pF2->m_Date));
}

int TriBoite(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;
char szCleaned1[20],szCleaned2[20];

	return(_stricmp(RemoveSpaces(pF1->m_Boite,szCleaned1,sizeof(szCleaned1)),RemoveSpaces(pF2->m_Boite,szCleaned2,sizeof(szCleaned2))));
}

int TriRangee(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return((int)pF1->m_nRangee-(int)pF2->m_nRangee);
}

int TriNumero(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return((int)pF1->m_nNumero-(int)pF2->m_nNumero);
}

int TriSujetDias(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_SujetDias,pF2->m_SujetDias));
}

int TriAgrandi(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return((int)pF1->m_bAgrandi-(int)pF2->m_bAgrandi);
}

int TriClasse(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return((int)pF1->m_bClasse-(int)pF2->m_bClasse);
}

int TriVerifie(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return((int)pF1->m_bVerifie-(int)pF2->m_bVerifie);
}

int TriCommentaire(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_Commentaire,pF2->m_Commentaire));
}


int TriCameraDigitale(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return((int)pF1->m_bCameraDigitale-(int)pF2->m_bCameraDigitale);
}

int TriPremierNiveau(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_PremierNiveau,pF2->m_PremierNiveau));
}

int TriSecondNiveau(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_SecondNiveau,pF2->m_SecondNiveau));
}

int TriTroisiemeNiveau(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_TroisiemeNiveau,pF2->m_TroisiemeNiveau));
}

int TriNomFichier(const void *p1, const void *p2)
{
const CFicheDias *pF1=(const CFicheDias *)p1;
const CFicheDias *pF2=(const CFicheDias *)p2;

	return(_stricmp(pF1->m_NomFichierJpeg,pF2->m_NomFichierJpeg));
}

void PrepareCritereBoiteRangeeNumero(std::string &p_critere,const CFicheDias *p_pDias)
{
char l_szTmp[64];
	
	p_critere.reserve(50);
	
	if (!p_pDias->m_bCameraDigitale)
	{
		//Les dias d'abord.

		/*Il y a un problème avec les maldives: l'ordre chronologique n'est pas celui
		des rangées-->faisons un petit cas spécial et évitons par la suite de refaire
		un coup pareil...*/
		int l_nRangee=p_pDias->m_nRangee;
		if (p_pDias->m_Sujet=="MEHDI VACANCES AUX MALDIVES 28/09 au 06/10/2000" && l_nRangee==2)
			l_nRangee=7;

		p_critere=RemoveSpaces(p_pDias->m_Boite,l_szTmp,sizeof(l_szTmp));
		_snprintf_s(l_szTmp,sizeof(l_szTmp),sizeof(l_szTmp),"%02d%03d",l_nRangee,p_pDias->m_nNumero);
		p_critere.append(l_szTmp);
	}
	else
	{
		//Les digitales ensuite
		p_critere="ZZZ";
		p_critere.append(p_pDias->m_PremierNiveau);
		p_critere.append(p_pDias->m_SecondNiveau);
		p_critere.append(p_pDias->m_TroisiemeNiveau);
		if (p_pDias->m_NomFichierJpeg.GetLength())
			p_critere.append(p_pDias->m_NomFichierJpeg);
		else
		{
			_snprintf_s(l_szTmp,sizeof(l_szTmp),sizeof(l_szTmp),"%06d",p_pDias->m_nNumero);
			p_critere.append(l_szTmp);
		}
	}
}

int TriBoiteRangeeNumero(const void *p1, const void *p2)
{
std::string szBuf1,szBuf2;

	PrepareCritereBoiteRangeeNumero(szBuf1,(const CFicheDias *)p1);
	PrepareCritereBoiteRangeeNumero(szBuf2,(const CFicheDias *)p2);

	return(_stricmp(szBuf1.c_str(),szBuf2.c_str()));
}

void CAccessDiasDlg::OnManipulationTrier() 
{
CDlgCritereTri Dlg;
CArray <CFicheDias,CFicheDias> &Dias=m_Banque.m_Dias;
CFicheDias *pData=&Dias.ElementAt(0);

	if (!UpdateData())
		return;

	if (Dlg.DoModal()!=IDOK)
		return;

	switch (Dlg.m_nIdxChamp) {
		case 0:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriSujet);
			break;
		case 1:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriDate);
			break;
		case 2:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriBoite);
			break;
		case 3:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriRangee);
			break;
		case 4:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriNumero);
			break;
		case 5:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriSujetDias);
			break;
		case 6:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriAgrandi);
			break;
		case 7:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriClasse);
			break;
		case 8:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriVerifie);
			break;
		case 9:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriCommentaire);
			break;
		case 10:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriCameraDigitale);
			break;
		case 11:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriPremierNiveau);
			break;
		case 12:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriSecondNiveau);
			break;
		case 13:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriTroisiemeNiveau);
			break;
		case 14:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriNomFichier);
			break;
		case 15:
			qsort(pData,Dias.GetSize(),sizeof(CFicheDias),TriBoiteRangeeNumero);
			break;
		default:
			MessageBox("Il faudrait penser à ajouter le critère","Tri");
			break;
	}
	m_nNoFiche=0;
	UpdateBoutons();
}

char *GetNextToken(char *&pszToTokenize,const char *pszSep)
{
	char *pszEndToken=strstr(pszToTokenize,pszSep);
	char *pszToReturn=pszToTokenize;

	if (pszEndToken)
	{
		*pszEndToken=0;
		pszToTokenize=pszEndToken+1;
	}
	return pszToReturn;

}

void CAccessDiasDlg::OnFichierImporteFichierTexte() 
{
CFileDialog Dlg(1, "txt", NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT,
		"Fichier texte|*.txt||",this);

	if (Dlg.DoModal()==IDCANCEL)
		return;

	FILE *hf=NULL;
	fopen_s(&hf,Dlg.GetPathName(),"rt");
	if (!hf)
	{
		MessageBox("Impossible d'ouvrir le fichier","Import");
		return;
	}
	char szLine[4096];
	
	//Skip title line
	fgets(szLine,sizeof(szLine),hf);

	while (fgets(szLine,sizeof(szLine),hf))
	{
		//Clean the line
		CString Ligne(szLine);
		Ligne.TrimRight(" \\r\\n");
		Ligne.TrimLeft(' ');
		if (!Ligne.GetLength())
			continue;
		//Get record content (must have all fields in CAccessDiasApp::szChamps order)
		StringCchCopy(szLine,sizeof(szLine),Ligne);
		
		/*Ajoute*/
		int l_nAncienneTaille=m_Banque.m_Dias.GetSize();
		m_Banque.m_Dias.SetSize(l_nAncienneTaille+1);
		CFicheDias &Dia=m_Banque.m_Dias[l_nAncienneTaille];

		/*Affecte les champs*/
		char *pszToTokenize=szLine;
		Dia.m_Sujet=GetNextToken(pszToTokenize,"\\t");
		Dia.m_Date=GetNextToken(pszToTokenize,"\\t");
		Dia.m_Boite=GetNextToken(pszToTokenize,"\\t");
		Dia.m_nRangee=atoi(GetNextToken(pszToTokenize,"\\t"));
		Dia.m_nNumero=atoi(GetNextToken(pszToTokenize,"\\t"));
		Dia.m_SujetDias=GetNextToken(pszToTokenize,"\\t");
		Dia.m_bAgrandi=strstr(GetNextToken(pszToTokenize,"\\t"),"V") ? 1:0;
		Dia.m_bClasse=strstr(GetNextToken(pszToTokenize,"\\t"),"V") ? 1:0;
		Dia.m_bVerifie=strstr(GetNextToken(pszToTokenize,"\\t"),"V") ? 1:0;
		Dia.m_Commentaire=GetNextToken(pszToTokenize,"\\t");
		Dia.m_bCameraDigitale=strstr(GetNextToken(pszToTokenize,"\\t"),"V") ? 1:0;
		Dia.m_PremierNiveau=GetNextToken(pszToTokenize,"\\t");
		Dia.m_SecondNiveau=GetNextToken(pszToTokenize,"\\t");
		Dia.m_TroisiemeNiveau=GetNextToken(pszToTokenize,"\\t");
		Dia.m_NomFichierJpeg=GetNextToken(pszToTokenize,"\\t");
	}
	fclose(hf);

}

void CAccessDiasDlg::OnEffaceFicheVides() 
{
	if (MessageBox("Etes-vous sur de supprimer les fiches vides ?","Dias",MB_YESNO|MB_ICONQUESTION)==IDNO)
		return;

	for (int nCompt=0;nCompt<m_Banque.GetTaille();nCompt++)
	{
		const CFicheDias &l_Cur=m_Banque.m_Dias[nCompt];
		if (!l_Cur.m_Sujet.GetLength() && !l_Cur.m_SujetDias.GetLength() &&
			!l_Cur.m_Date.GetLength() && !l_Cur.m_Commentaire.GetLength())
		{
			m_Banque.m_Dias.RemoveAt(nCompt);
			nCompt--;
		}
	}

	//Vérifie qu'il y a au-moins une fiche
	if (!m_Banque.GetTaille())
		m_Banque.CreeFiche();

	if (m_nNoFiche>=m_Banque.GetTaille())
		m_nNoFiche=m_Banque.GetTaille()-1;

	UpdateBoutons();
	m_bSauve=0;
}

void CAccessDiasDlg::OnFichierFusionner() 
{
	CBanqueDias l_Banque;
	
	{
		//Nom du fichier
		CFileDialog Dlg(1, "bdd", NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT,
				"Données dias|*.bdd||",this);

		if (Dlg.DoModal()==IDCANCEL)
			return;
		
		//Le lit
		l_Banque.LitBanque(Dlg.GetPathName());
	}

	//Demande le critère pour fusionner
	CDlgRecherche Dlg(this);	

	if (Dlg.DoModal()==IDCANCEL)
		return;

	if (!Dlg.m_ValChamp[0].GetLength() && !Dlg.m_ValChamp[1].GetLength()
		 && !Dlg.m_ValChamp[2].GetLength()) {
		MessageBox("Critère invalide");
		return;
	}

	/*Fait la recherche*/
	int nCompt;
	int l_nTailleBanque=l_Banque.GetTaille();

	for (nCompt=0;nCompt<l_nTailleBanque;nCompt++)
	{
		/*Trouvé*/
		if (l_Banque.CorrespondsCritere(nCompt,Dlg.m_ValChamp,Dlg.m_nChamp))
		{
			/*Ajoute*/
			int l_nAncienneTaille=m_Banque.m_Dias.GetSize();
			m_Banque.m_Dias.SetSize(l_nAncienneTaille+1);
			m_Banque.m_Dias[l_nAncienneTaille]=l_Banque.m_Dias[nCompt];
		}
	}

	UpdateBoutons();
	m_bSauve=0;
}

void CAccessDiasDlg::OnEffaceCritere() 
{
	//Demande le critère pour effacer
	CDlgRecherche Dlg(this);	

	if (Dlg.DoModal()==IDCANCEL)
		return;

	if (!Dlg.m_ValChamp[0].GetLength() && !Dlg.m_ValChamp[1].GetLength()
		 && !Dlg.m_ValChamp[2].GetLength()) {
		MessageBox("Critère invalide");
		return;
	}

	/*Fait le nettoyage*/
	int nCompt;
	int l_nTailleBanque=m_Banque.GetTaille();
	for (nCompt=0;nCompt<l_nTailleBanque;nCompt++)
	{
		/*Trouvé*/
		if (m_Banque.CorrespondsCritere(nCompt,Dlg.m_ValChamp,Dlg.m_nChamp))
		{
			/*Efface*/
			m_Banque.m_Dias.RemoveAt(nCompt);
			l_nTailleBanque--;
			nCompt--;
		}
	}

	//Vérifie qu'il y a au-moins une fiche
	if (!l_nTailleBanque)
	{
		m_Banque.CreeFiche();
		l_nTailleBanque++;
	}
	
	if (m_nNoFiche>=l_nTailleBanque)
		m_nNoFiche=l_nTailleBanque-1;

	UpdateBoutons();
	m_bSauve=0;
}

void CreateDirRecursive(const char *p_pszDir)
{
	std::string l_Dir(p_pszDir);
	size_t l_nLen=l_Dir.length();

	//Nothing left
	if (l_nLen<1)
		return;
	
	//Remove final slash
	if (l_Dir[l_nLen-1]=='/' || l_Dir[l_nLen-1]=='\\')
	{
		l_Dir=l_Dir.substr(0,l_nLen-1);
		l_nLen--;
		
		//Nothing left
		if (l_nLen<1)
			return;
	}
	size_t l_nSlash=l_Dir.find_last_of('\\');
	std::string l_NextLevel(l_Dir);
	if (l_nSlash!=std::string::npos)
	{
		l_NextLevel=l_Dir.substr(0,l_nSlash);
		CreateDirRecursive(l_NextLevel.c_str());
	}
	CreateDirectory(l_Dir.c_str(),NULL);
}

void CAccessDiasDlg::OnOutilsPrepareEntreesJpegs() 
{
	CNewJpegSerie dlg(this);
	if (dlg.DoModal()!=IDOK)
		return;

	if (!dlg.m_Date.GetLength() || !dlg.m_Subject.GetLength())
	{
		MessageBox("Un sujet et une date sont nécessaires","Dias");
		return;
	}

	//Root dir
	std::string l_DiasDir;
	GetDiasRootDir(l_DiasDir);
	
	//Scans dir
	std::string l_ScansDir(l_DiasDir);
	l_ScansDir+="scans\\";

	//Ask jpeg dir
	CFileDialog l_FileDlg(true, "jpg", NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT,
		"Fichiers jpeg|*.jpg||",this);

	l_FileDlg.m_ofn.lpstrInitialDir=l_ScansDir.c_str();
	if (l_FileDlg.DoModal()!=IDOK)
		return;
	
	//Check that the jpeg is in scans subdir of dias dir
	std::string l_JpegPath(l_FileDlg.GetPathName());
	if (_strnicmp(l_JpegPath.c_str(),l_ScansDir.c_str(),l_ScansDir.length()))
	{
		MessageBox("Le jpeg choisi doit être dans le sous-répertoire scans du répertoire dias","Dias");
		return;
	}
	
	//Extract the relative path
	l_JpegPath=l_JpegPath.substr(l_ScansDir.length());
	size_t l_nLastSlash=l_JpegPath.find_last_of('\\');
	l_JpegPath=l_JpegPath.substr(0,l_nLastSlash);
	
	//Split it into its levels
	std::string l_Dirpart1,l_Dirpart2,l_Dirpart3;
	size_t l_Slash1=l_JpegPath.find('\\');
	if (l_Slash1!=std::string::npos)
	{
		l_Dirpart1=l_JpegPath.substr(0,l_Slash1);
		size_t l_Slash2=l_JpegPath.find('\\',l_Slash1+1);
		if (l_Slash2!=std::string::npos)
		{
			l_Dirpart2=l_JpegPath.substr(l_Slash1+1,l_Slash2-l_Slash1-1);
			l_Dirpart3=l_JpegPath.substr(l_Slash2+1);
		}
		else
			l_Dirpart2=l_JpegPath.substr(l_Slash1+1);
	}
	else
		l_Dirpart1=l_JpegPath;

	if (l_Dirpart3.find('\\')!=std::string::npos)
	{
		MessageBox("Le niveau max de sous-répertoires est de trois","Dias");
		return;
	}

	//Enumerate all files
	std::string l_mask=l_ScansDir+l_JpegPath+"\\*.*";
	WIN32_FIND_DATA l_FileData;
	HANDLE l_hFindFile=INVALID_HANDLE_VALUE;
	
	int l_nAddedRecords=0;
	while (true)
	{
		if (l_hFindFile==INVALID_HANDLE_VALUE)
		{
			l_hFindFile=FindFirstFile(l_mask.c_str(),&l_FileData);
			if (l_hFindFile==INVALID_HANDLE_VALUE)
				break;
		}
		else
		{
			if (!FindNextFile(l_hFindFile,&l_FileData))
				break;
		}

		CString l_UpperName=l_FileData.cFileName;
		l_UpperName.MakeUpper();

		//Is it a jpeg?
		if (!strstr((LPCSTR)l_UpperName,".JPG"))
			continue;

		//Prepare the record
		m_Banque.CreeFiche(false);
		int l_nRecords=m_Banque.GetTaille();

		m_Banque.m_Dias[l_nRecords-1].m_Sujet=dlg.m_Subject;
		m_Banque.m_Dias[l_nRecords-1].m_Date=dlg.m_Date;
		m_Banque.m_Dias[l_nRecords-1].m_nNumero=++l_nAddedRecords;
		m_Banque.m_Dias[l_nRecords-1].m_bAgrandi=true;
		m_Banque.m_Dias[l_nRecords-1].m_bCameraDigitale=true;
		m_Banque.m_Dias[l_nRecords-1].m_PremierNiveau=l_Dirpart1.c_str();
		m_Banque.m_Dias[l_nRecords-1].m_SecondNiveau=l_Dirpart2.c_str();
		m_Banque.m_Dias[l_nRecords-1].m_TroisiemeNiveau=l_Dirpart3.c_str();
		m_Banque.m_Dias[l_nRecords-1].m_NomFichierJpeg=l_FileData.cFileName;
		m_Banque.m_Dias[l_nRecords-1].m_Commentaire=dlg.m_Commentaire;
	}	
	if (l_hFindFile!=INVALID_HANDLE_VALUE)
		FindClose(l_hFindFile);
	
	if (l_nAddedRecords>0)
	{
		//Go back to first added record
		m_nNoFiche=m_Banque.GetTaille()-l_nAddedRecords;

		UpdateBoutons();
		m_bSauve=0;

		//Create directory
		std::string l_BatchDir=l_DiasDir+l_JpegPath;
		CreateDirRecursive(l_BatchDir.c_str());

		//Prepare batch for html generation
		std::string l_BatchPath=l_BatchDir+"\\preparehtml.bat";

		FILE *l_hf=NULL;
		fopen_s(&l_hf,l_BatchPath.c_str(),"wt");
		if (!l_hf)
		{
			MessageBox((std::string("Fiches créées, mais impossible de générer ")+l_BatchPath).c_str(),"Dias");
			return;
		}
		fprintf(l_hf,"%%2prephtml\\Release\\prephtml %%0 %%1 \"%s\"",(const char *)dlg.m_Subject);
		fclose(l_hf);
	}
}


void CAccessDiasDlg::OnOutilsGenereJpegs() 
{
	int l_nTailleBanque=m_Banque.GetTaille();
	if (l_nTailleBanque)
	{
		CFicheDias &Dia=m_Banque.m_Dias[m_nNoFiche];
		if (!(Dia.m_bCameraDigitale && Dia.m_PremierNiveau.GetLength()))
		{
			MessageBox("L'image ne provient pas d'un appareil numérique","Dias");
			return;
		}

		//Root dir
		std::string l_DiasDir;
		GetDiasRootDir(l_DiasDir);

		//Save the db
		OnFichierSauver();

		//Converter dir
		std::string l_ConverterPath;
		l_ConverterPath=l_DiasDir+"ResizeJpegs\\ResizeJpegs\\bin\\Release\\ResizeJpegs.exe";

		std::string l_JpegPath=Dia.m_PremierNiveau;
		if (Dia.m_SecondNiveau.GetLength())
		{
			l_JpegPath+="\\";
			l_JpegPath+=Dia.m_SecondNiveau;
		}
		if (Dia.m_TroisiemeNiveau.GetLength())
		{
			l_JpegPath+="\\";
			l_JpegPath+=Dia.m_TroisiemeNiveau;
		}
		if (_access(l_ConverterPath.c_str(),0)!=0)
		{
			MessageBox((std::string("Impossible de convertir, il n'y a pas de fichier ")+l_ConverterPath).c_str(),"Dias");
			return;
		}

		//Launch
		const char *l_args[]={"converter.exe",l_JpegPath.c_str(),"y", "notifdir", l_DiasDir.c_str(),NULL};
		if (_spawnv(_P_WAIT, l_ConverterPath.c_str(), l_args)!=0)
			MessageBox((std::string("Images non converties, erreur dans le lancement de ")+l_ConverterPath).c_str(),"Dias");
	}
	else
		MessageBox("Base vide: pas d'images à convertir","Dias");
}


void CAccessDiasDlg::OnOutilsCreeCommentHtml() 
{
	int l_nTailleBanque=m_Banque.GetTaille();
	if (l_nTailleBanque)
	{
		CFicheDias &Dia=m_Banque.m_Dias[m_nNoFiche];
		if (!Dia.m_PremierNiveau.GetLength())
		{
			MessageBox("Le chemin des fichiers n'est pas fourni dans l'enregistrement","Dias");
			return;
		}

		//Root dir
		std::string l_DiasDir;
		GetDiasRootDir(l_DiasDir);

		//Save the db
		OnFichierSauver();
		
		//Path where is the batch
		std::string l_BatchPath(l_DiasDir);

		l_BatchPath+=Dia.m_PremierNiveau;
		l_BatchPath+="\\";
		if (Dia.m_SecondNiveau.GetLength())
		{
			l_BatchPath+=Dia.m_SecondNiveau;
			l_BatchPath+="\\";
		}
		if (Dia.m_TroisiemeNiveau.GetLength())
		{
			l_BatchPath+=Dia.m_TroisiemeNiveau;
			l_BatchPath+="\\";
		}
		l_BatchPath+="preparehtml.bat";
		if (_access(l_BatchPath.c_str(),0)!=0)
		{
			MessageBox((std::string("Impossible de générer, il n'y a pas de fichier ")+l_BatchPath).c_str(),"Dias");
			return;
		}

		//Launch
		const char *l_args[]={l_BatchPath.c_str(),(const char *)m_NomFichier,l_DiasDir.c_str(), NULL};
		if (_spawnv(_P_WAIT, l_BatchPath.c_str(), l_args)!=0)
		{
			char l_szErrorCode[16];
			_itoa_s(errno,l_szErrorCode,sizeof(l_szErrorCode),10);
			MessageBox((std::string("Commentaires non régénérés, erreur dans le lancement de ")+l_BatchPath+", error code is "+l_szErrorCode).c_str(),"Dias");
		}
	}
	else
		MessageBox("Base vide: pas de commentaire à générer","Dias");
}

void CAccessDiasDlg::OnOutilsRecreeToutLesCommentaires() 
{
	//Root dir
	std::string l_DiasDir;
	GetDiasRootDir(l_DiasDir);

	//Save the db
	OnFichierSauver();

	std::string l_ExePath(l_DiasDir);
	l_ExePath+="generate_all_comments\\Release\\generate_all_comments.exe";
	if (_access(l_ExePath.c_str(),0)!=0)
	{
		MessageBox((std::string("Impossible de générer, il n'y a pas de programme ")+l_ExePath).c_str(),"Dias");
		return;
	}

	//Launch
	const char *l_args[]={l_ExePath.c_str(),l_DiasDir.c_str(), NULL};
	if (_spawnv(_P_WAIT, l_ExePath.c_str(), l_args)!=0)
	{
		char l_szErrorCode[16];
		_itoa_s(errno,l_szErrorCode,sizeof(l_szErrorCode),10);
		MessageBox((std::string("Commentaires non régénérés, erreur dans le lancement de ")+l_ExePath+", error code is "+l_szErrorCode).c_str(),"Dias");
	}
}

void CAccessDiasDlg::GetDiasRootDir(std::string &p_RootDir,bool p_bCanShowDlg)
{
	p_RootDir=GetRegistryValue("DiasRootDir");
	
	if (p_RootDir.empty() && p_bCanShowDlg)
	{
		OnFichierRepertoiredias();
		GetDiasRootDir(p_RootDir);
	}
}

std::string GetNiveaux(const CString &PremierNiveau,const CString &SecondNiveau,const CString &TroisiemeNiveau)
{
	std::string Niveaux;

	if (!PremierNiveau.IsEmpty())
	{
		Niveaux+=PremierNiveau;
		Niveaux+="\\";
	}
	if (!SecondNiveau.IsEmpty())
	{
		Niveaux+=SecondNiveau;
		Niveaux+="\\";
	}
	if (!TroisiemeNiveau.IsEmpty())
	{
		Niveaux+=TroisiemeNiveau;
		Niveaux+="\\";
	}

	return Niveaux;
}

void CAccessDiasDlg::OnRenommerFichier() 
{
	if (!UpdateData())
		return;

	int l_nTailleBanque=m_Banque.GetTaille();
	if (l_nTailleBanque)
	{
		if (!m_NomFichierJpeg.IsEmpty())
		{
			CDlgRenommerImage l_DlgNouveauNom(this);
			l_DlgNouveauNom.m_NouveauNom=m_NomFichierJpeg;
			if (l_DlgNouveauNom.DoModal()==IDOK)
			{
				std::string l_DiasDir;
				GetDiasRootDir(l_DiasDir);

				std::string Niveaux=GetNiveaux(m_PremierNiveau,m_SecondNiveau,m_TroisiemeNiveau);

				MoveFile((l_DiasDir+"scans\\"+Niveaux+(LPCSTR)m_NomFichierJpeg).c_str(),
					(l_DiasDir+"scans\\"+Niveaux+(LPCSTR)l_DlgNouveauNom.m_NouveauNom).c_str());
				MoveFile((l_DiasDir+Niveaux+"view\\"+(LPCSTR)m_NomFichierJpeg).c_str(),
					(l_DiasDir+Niveaux+"view\\"+(LPCSTR)l_DlgNouveauNom.m_NouveauNom).c_str());
				MoveFile((l_DiasDir+Niveaux+"big\\"+(LPCSTR)m_NomFichierJpeg).c_str(),
					(l_DiasDir+Niveaux+"big\\"+(LPCSTR)l_DlgNouveauNom.m_NouveauNom).c_str());
				MoveFile((l_DiasDir+Niveaux+"ContactSheet\\"+(LPCSTR)m_NomFichierJpeg).c_str(),
					(l_DiasDir+Niveaux+"ContactSheet\\"+(LPCSTR)l_DlgNouveauNom.m_NouveauNom).c_str());

				m_NomFichierJpeg=l_DlgNouveauNom.m_NouveauNom;
				UpdateData(FALSE);
			}
		}
	}
}

void CAccessDiasDlg::OnOutilsCompleteEntreesJpegs() 
{
	if (!UpdateData())
		return;

	/*Prends l'ensemble des fiches avec les sujet courant*/
	int nCompt;
	int l_nTailleBanque=m_Banque.GetTaille();
	std::set<std::string> l_Existant;
	for (nCompt=0;nCompt<l_nTailleBanque;nCompt++)
	{
		const CFicheDias &l_Cur=m_Banque.m_Dias[nCompt];
		
		if (l_Cur.m_Sujet==m_Sujet)
		{
			//Insert in upper case, we will search also on upper case, avoid inserting in only case changes
			CString l_UpperName=l_Cur.m_NomFichierJpeg;
			l_UpperName.MakeUpper();
			l_Existant.insert((LPCSTR)l_UpperName);
		}
	}
	if (l_Existant.empty())
		return;
	
	//Root dir
	std::string l_DiasDir;
	GetDiasRootDir(l_DiasDir);
	
	//Scans dir
	std::string l_ScansDir(l_DiasDir);
	l_ScansDir+="scans\\";

	//Enumerate all files
	std::string l_mask=l_ScansDir+GetNiveaux(m_PremierNiveau,m_SecondNiveau,m_TroisiemeNiveau)+"*.*";
	WIN32_FIND_DATA l_FileData;
	HANDLE l_hFindFile=INVALID_HANDLE_VALUE;
	
	while (true)
	{
		if (l_hFindFile==INVALID_HANDLE_VALUE)
		{
			l_hFindFile=FindFirstFile(l_mask.c_str(),&l_FileData);
			if (l_hFindFile==INVALID_HANDLE_VALUE)
				break;
		}
		else
		{
			if (!FindNextFile(l_hFindFile,&l_FileData))
				break;
		}

		CString l_UpperName=l_FileData.cFileName;
		l_UpperName.MakeUpper();

		//Is it a jpeg?
		if (!strstr((LPCSTR)l_UpperName,".JPG"))
			continue;

		//If already present, ignore
		if (l_Existant.find((LPCSTR)l_UpperName)!=l_Existant.end())
			continue;

		//Prepare the record
		m_Banque.CreeFiche(false);
		int l_nRecords=m_Banque.GetTaille();

		m_Banque.m_Dias[l_nRecords-1].m_Sujet=m_Sujet;
		m_Banque.m_Dias[l_nRecords-1].m_Date=m_Date;
		m_Banque.m_Dias[l_nRecords-1].m_nNumero=0;	//Done later
		m_Banque.m_Dias[l_nRecords-1].m_bAgrandi=true;
		m_Banque.m_Dias[l_nRecords-1].m_bCameraDigitale=true;
		m_Banque.m_Dias[l_nRecords-1].m_PremierNiveau=m_PremierNiveau;
		m_Banque.m_Dias[l_nRecords-1].m_SecondNiveau=m_SecondNiveau;
		m_Banque.m_Dias[l_nRecords-1].m_TroisiemeNiveau=m_TroisiemeNiveau;
		m_Banque.m_Dias[l_nRecords-1].m_NomFichierJpeg=l_FileData.cFileName;
		m_Banque.m_Dias[l_nRecords-1].m_Commentaire=m_Commentaire;
	}	
	if (l_hFindFile!=INVALID_HANDLE_VALUE)
		FindClose(l_hFindFile);

	//Sort never hurts
	qsort(&m_Banque.m_Dias.ElementAt(0),m_Banque.m_Dias.GetSize(),sizeof(CFicheDias),TriBoiteRangeeNumero);

	//Recreate all numbers
	l_nTailleBanque=m_Banque.GetTaille();
	int l_nCurrentNumber=1;
	int l_nFirstSubjectRecord=-1;
	for (nCompt=0;nCompt<l_nTailleBanque;nCompt++)
	{
		CFicheDias &l_Cur=m_Banque.m_Dias[nCompt];
		
		if (l_Cur.m_Sujet==m_Sujet)
		{
			if (l_nFirstSubjectRecord<0)
				l_nFirstSubjectRecord=nCompt;

			l_Cur.m_nNumero=l_nCurrentNumber;
			l_nCurrentNumber++;
		}
	}

	
	//Go back to first record of this serie
	if (l_nFirstSubjectRecord>=0)
		m_nNoFiche=l_nFirstSubjectRecord;
	else
		m_nNoFiche=0;

	UpdateBoutons();
	m_bSauve=0;
}

void CAccessDiasDlg::OnFichierRepertoiredias()
{
	/*Récupère le nom du dernier fichier chargé*/
	std::string szNom;
	
	GetDiasRootDir(szNom,false);

	CFileDialog Dlg(1, "html", !szNom.empty() ? szNom.c_str():NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT,
		"Dias root dir|index.html||",this);

	if (Dlg.DoModal()==IDCANCEL)
		return;

	char l_Path[256];
	StringCchCopy(l_Path,sizeof(l_Path),(LPCTSTR)Dlg.GetPathName());
	strrchr(l_Path,'\\')[1]=0;

	/*Sauve le nom*/
	SaveRegistryValue("DiasRootDir",l_Path);
}

void CAccessDiasDlg::OnManipulationMetajourCommentaire()
{
	//Demande le critère pour MAJ
	CDlgRecherche Dlg(this);	

	if (Dlg.DoModal()==IDCANCEL)
		return;

	if (!Dlg.m_ValChamp[0].GetLength() && !Dlg.m_ValChamp[1].GetLength()
		 && !Dlg.m_ValChamp[2].GetLength()) {
		MessageBox("Critère invalide");
		return;
	}

	//Get desired comment
	CDlgUpdateComment l_DlgComment(this);
	if (l_DlgComment.DoModal()==IDCANCEL)
		return;

	/*Adapte*/
	int nCompt;
	int l_nTailleBanque=m_Banque.GetTaille();
	for (nCompt=0;nCompt<l_nTailleBanque;nCompt++)
	{
		/*Trouvé*/
		if (m_Banque.CorrespondsCritere(nCompt,Dlg.m_ValChamp,Dlg.m_nChamp))
			m_Banque.m_Dias[nCompt].m_Commentaire=l_DlgComment.m_Comment;
	}

	UpdateBoutons();
	m_bSauve=0;
}
