// dlgallera.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CDlgAllerA dialog

class CDlgAllerA : public CDialog
{
// Construction
public:
	CDlgAllerA(CWnd* pParent,int nFicheCour,int nMaximum);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CDlgAllerA)
	enum { IDD = IDD_ALLERA };
	UINT	m_nNoFiche;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CDlgAllerA)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	int m_nMaximum;
	// Generated message map functions
	//{{AFX_MSG(CDlgAllerA)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};
