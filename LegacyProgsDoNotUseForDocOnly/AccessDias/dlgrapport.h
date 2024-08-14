// dlgrapport.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CDlgRapport dialog

class CDlgRapport : public CDialog
{
// Construction
public:
	CDlgRapport(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CDlgRapport)
	enum { IDD = IDD_RAPPORT };
	//}}AFX_DATA
	int		m_nChamp[3];
	CString	m_ValChamp[3];

	int m_bRapport;
	int m_bEtiquettes;
	int m_bCompte;


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CDlgRapport)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CDlgRapport)
	virtual BOOL OnInitDialog();
	virtual void OnOK();
	afx_msg void OnSelchangeListechamps1();
	afx_msg void OnSelchangeListechamps2();
	afx_msg void OnSelchangeListechamps3();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};
