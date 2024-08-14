// dlgrecherche.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CDlgRecherche dialog

class CDlgRecherche : public CDialog
{
// Construction
public:
	CDlgRecherche(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CDlgRecherche)
	enum { IDD = IDD_RECHERCHE };
	//}}AFX_DATA
 	int		m_nChamp[3];
	CString	m_ValChamp[3];


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CDlgRecherche)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CDlgRecherche)
	virtual BOOL OnInitDialog();
	afx_msg void OnSelchangeListechamps1();
	afx_msg void OnSelchangeListechamps2();
	afx_msg void OnSelchangeListechamps3();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};
