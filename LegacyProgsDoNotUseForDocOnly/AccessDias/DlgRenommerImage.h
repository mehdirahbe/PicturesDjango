#if !defined(AFX_DLGRENOMMERIMAGE_H__A2CC3492_138A_4288_A589_67D7623B1010__INCLUDED_)
#define AFX_DLGRENOMMERIMAGE_H__A2CC3492_138A_4288_A589_67D7623B1010__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// DlgRenommerImage.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CDlgRenommerImage dialog

class CDlgRenommerImage : public CDialog
{
// Construction
public:
	CDlgRenommerImage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CDlgRenommerImage)
	enum { IDD = IDD_GLG_RENOMMER_IMAGE };
	CString	m_NouveauNom;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CDlgRenommerImage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CDlgRenommerImage)
		// NOTE: the ClassWizard will add member functions here
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_DLGRENOMMERIMAGE_H__A2CC3492_138A_4288_A589_67D7623B1010__INCLUDED_)
