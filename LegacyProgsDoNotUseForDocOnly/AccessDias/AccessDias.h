// AccessDias.h : main header file for the ACCESSDIAS application
//

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CAccessDiasApp:
// See AccessDias.cpp for the implementation of this class
//

class CAccessDiasApp : public CWinApp
{
public:
	static const char * szChamps[];
	static int m_nNbreChampsRecherches;
	static int m_nNbreChampsTris;
	CAccessDiasApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAccessDiasApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CAccessDiasApp)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////
