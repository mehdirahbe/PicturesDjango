// DlgCritereTri.cpp : implementation file
//

#include "stdafx.h"
#include "AccessDias.h"
#include "DlgCritereTri.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CDlgCritereTri dialog


CDlgCritereTri::CDlgCritereTri(CWnd* pParent /*=NULL*/)
	: CDialog(CDlgCritereTri::IDD, pParent)
{
	//{{AFX_DATA_INIT(CDlgCritereTri)
	m_nIdxChamp = -1;
	//}}AFX_DATA_INIT
}


void CDlgCritereTri::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CDlgCritereTri)
	DDX_CBIndex(pDX, IDC_CRITERETRI, m_nIdxChamp);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CDlgCritereTri, CDialog)
	//{{AFX_MSG_MAP(CDlgCritereTri)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CDlgCritereTri message handlers

BOOL CDlgCritereTri::OnInitDialog() 
{
CComboBox *pCb=(CComboBox *)GetDlgItem(IDC_CRITERETRI);
int nCompt;
CAccessDiasApp *pApp=(CAccessDiasApp *)AfxGetApp();

	CDialog::OnInitDialog();
	
	// TODO: Add extra initialization here
	/*Remplit la combo*/
	for (nCompt=0;nCompt<pApp->m_nNbreChampsTris;nCompt++)
		pCb->AddString(pApp->szChamps[nCompt]);
	pCb->SetCurSel(0);

	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}
