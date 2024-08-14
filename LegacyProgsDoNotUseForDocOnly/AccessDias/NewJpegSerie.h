#if !defined(AFX_NEWJPEGSERIE_H__52C8F683_A20F_4133_9C6C_F9C6E9ADDE24__INCLUDED_)
#define AFX_NEWJPEGSERIE_H__52C8F683_A20F_4133_9C6C_F9C6E9ADDE24__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// NewJpegSerie.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CNewJpegSerie dialog

class CNewJpegSerie : public CDialog
{
// Construction
public:
	CNewJpegSerie(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CNewJpegSerie)
	enum { IDD = IDD_NEW_JPEG_SERIE };
	CString	m_Subject;
	CString	m_Date;
	CString	m_Commentaire;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CNewJpegSerie)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CNewJpegSerie)
	virtual void OnOK();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_NEWJPEGSERIE_H__52C8F683_A20F_4133_9C6C_F9C6E9ADDE24__INCLUDED_)
