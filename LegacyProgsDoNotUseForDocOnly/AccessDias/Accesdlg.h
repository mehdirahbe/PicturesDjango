// Accesdlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CAccessDiasDlg dialog

class CAccessDiasDlg : public CDialog
{
// Construction
public:
	CAccessDiasDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CAccessDiasDlg)
	enum { IDD = IDD_ACCESSDIAS_DIALOG };
	CString	m_Sujet;
	CString	m_Date;
	CString	m_Boite;
	UINT	m_nRangee;
	UINT	m_nNumero;
	CString	m_SujetDias;
	BOOL	m_bAgrandi;
	BOOL	m_bClasse;
	BOOL	m_bVerifie;
	CString	m_Commentaire;
	CString	m_Total;
	CString	m_NoFiche;
	BOOL m_bCameraDigitale;
	CString m_PremierNiveau;
	CString m_SecondNiveau;
	CString m_TroisiemeNiveau;
	CString m_NomFichierJpeg;
	//}}AFX_DATA

	int m_nNoFiche;
	CBanqueDias m_Banque;
	int m_bTakeLast;
	int m_bSauve;
	CString m_NomFichier;

	BOOL UpdateData(BOOL bSaveAndValidate = TRUE);

	std::string GetRegistryValue(const char *p_pszKey)
	{
		HKEY hKey;
		TCHAR szNom[_MAX_PATH]={_T("")};
		DWORD dwType,dwSize=sizeof(szNom);
		if (ERROR_SUCCESS==RegCreateKey(HKEY_CURRENT_USER,
			(std::string("AccessDias\\\\")+p_pszKey).c_str(),&hKey)) {
				RegQueryValueEx(hKey,NULL,0,&dwType,(LPBYTE)szNom,&dwSize);
				RegCloseKey(hKey);
		}

		return szNom;
	}

	void SaveRegistryValue(const char *p_pszKey,const char *p_pszValue)
	{
		HKEY hKey;
		if (ERROR_SUCCESS==RegCreateKey(HKEY_CURRENT_USER,
			(std::string("AccessDias\\\\")+p_pszKey).c_str(),&hKey)) {
			RegSetValueEx(hKey,NULL,0,REG_SZ,(CONST BYTE *)(LPCTSTR)p_pszValue,
			(strlen(p_pszValue)+1)*sizeof(TCHAR));
			RegCloseKey(hKey);
		}
	}

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAccessDiasDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	void UpdateBoutons();
	void MetAJourControles();
	void RecupereControles();
	CString &NettoieTexte(CString &Texte);
	void ImprimeRapport(HDC hDC,CString *pValChamp,int nChamp[3]);
	void ImprimeEtiquettes(HDC hDC,CString *pValChamp,int nChamp[3]);
	void GetDiasRootDir(std::string &p_RootDir,bool p_bCanShowDlg=true);

	// Generated message map functions
	//{{AFX_MSG(CAccessDiasDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnDeplacementsAvancer();
	afx_msg void OnDeplacementsDebut();
	afx_msg void OnDeplacementsFin();
	afx_msg void OnDeplacementsReculer();
	afx_msg void OnFichierCharger();
	afx_msg void OnFichierSauver();
	afx_msg void OnFichierQuitter();
	afx_msg void OnDeplacementsAller();
	afx_msg void OnManipulationEfface();
	afx_msg void OnManipulationReportelecontenu();
	virtual void OnCancel();
	afx_msg void OnManipulationRecherche();
	afx_msg void OnManipulationRapport();
	afx_msg void OnManipulationInserer();
	afx_msg void OnManipulationTrier();
	afx_msg void OnFichierImporteFichierTexte();
	afx_msg void OnEffaceFicheVides();
	afx_msg void OnFichierFusionner();
	afx_msg void OnEffaceCritere();
	afx_msg void OnOutilsPrepareEntreesJpegs();
	afx_msg void OnOutilsGenereJpegs();
	afx_msg void OnOutilsCreeCommentHtml();
	afx_msg void OnOutilsRecreeToutLesCommentaires();
	afx_msg void OnRenommerFichier();
	afx_msg void OnOutilsCompleteEntreesJpegs();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnFichierRepertoiredias();
public:
	afx_msg void OnManipulationMetajourCommentaire();
};
