// DlgCritereTri.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CDlgCritereTri dialog

class CDlgCritereTri : public CDialog
{
// Construction
public:
	CDlgCritereTri(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CDlgCritereTri)
	enum { IDD = IDD_CRITERETRI };
	int		m_nIdxChamp;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CDlgCritereTri)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CDlgCritereTri)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};
