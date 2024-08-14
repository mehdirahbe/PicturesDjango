// dlgallera.cpp : implementation file
//

#include "stdafx.h"
#include "AccessDias.h"
#include "dlgallera.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CDlgAllerA dialog


CDlgAllerA::CDlgAllerA(CWnd* pParent,int nFicheCour,int nMaximum)
	: CDialog(CDlgAllerA::IDD, pParent)
{
	m_nMaximum=nMaximum;
	//{{AFX_DATA_INIT(CDlgAllerA)
	m_nNoFiche = nFicheCour+1;
	//}}AFX_DATA_INIT
}


void CDlgAllerA::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CDlgAllerA)
	DDX_Text(pDX, IDC_NOFICHE, m_nNoFiche);
	DDV_MinMaxUInt(pDX, m_nNoFiche, 1, m_nMaximum);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CDlgAllerA, CDialog)
	//{{AFX_MSG_MAP(CDlgAllerA)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()


/////////////////////////////////////////////////////////////////////////////
// CDlgAllerA message handlers

BOOL CDlgAllerA::OnInitDialog() 
{
	CDialog::OnInitDialog();
	
	// TODO: Add extra initialization here
	GetDlgItem(IDC_NOFICHE)->SetFocus();
	
	return 0;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}
