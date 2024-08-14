// dlgrapport.cpp : implementation file
//

#include "stdafx.h"
#include "AccessDias.h"
#include "dlgrapport.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CDlgRapport dialog


CDlgRapport::CDlgRapport(CWnd* pParent /*=NULL*/)
	: CDialog(CDlgRapport::IDD, pParent)
{
	//{{AFX_DATA_INIT(CDlgRapport)
	//}}AFX_DATA_INIT
	m_nChamp[0] = -1;
	m_nChamp[1] = -1;
	m_nChamp[2] = -1;
	m_ValChamp[0] = _T("");
	m_ValChamp[1] = _T("");
	m_ValChamp[2] = _T("");
}


void CDlgRapport::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CDlgRapport)
	//}}AFX_DATA_MAP
	DDX_CBIndex(pDX, IDC_LISTECHAMPS1, m_nChamp[0]);
	DDX_CBIndex(pDX, IDC_LISTECHAMPS2, m_nChamp[1]);
	DDX_CBIndex(pDX, IDC_LISTECHAMPS3, m_nChamp[2]);
	DDX_Text(pDX, IDC_VALEUR1, m_ValChamp[0]);
	DDX_Text(pDX, IDC_VALEUR2, m_ValChamp[1]);
	DDX_Text(pDX, IDC_VALEUR3, m_ValChamp[2]);
}


BEGIN_MESSAGE_MAP(CDlgRapport, CDialog)
	//{{AFX_MSG_MAP(CDlgRapport)
	ON_CBN_SELCHANGE(IDC_LISTECHAMPS1, OnSelchangeListechamps1)
	ON_CBN_SELCHANGE(IDC_LISTECHAMPS2, OnSelchangeListechamps2)
	ON_CBN_SELCHANGE(IDC_LISTECHAMPS3, OnSelchangeListechamps3)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()


/////////////////////////////////////////////////////////////////////////////
// CDlgRapport message handlers

BOOL CDlgRapport::OnInitDialog() 
{
CComboBox *pCb1=(CComboBox *)GetDlgItem(IDC_LISTECHAMPS1);
CComboBox *pCb2=(CComboBox *)GetDlgItem(IDC_LISTECHAMPS2);
CComboBox *pCb3=(CComboBox *)GetDlgItem(IDC_LISTECHAMPS3);
int nCompt;
CAccessDiasApp *pApp=(CAccessDiasApp *)AfxGetApp();

	CDialog::OnInitDialog();
	
	// TODO: Add extra initialization here
	/*Remplit les combos*/
	for (nCompt=0;nCompt<pApp->m_nNbreChampsRecherches;nCompt++) {
		pCb1->AddString(pApp->szChamps[nCompt]);
		pCb2->AddString(pApp->szChamps[nCompt]);
		pCb3->AddString(pApp->szChamps[nCompt]);
	}
	pCb1->SetCurSel(0);
	pCb2->SetCurSel(0);
	pCb3->SetCurSel(0);

	CheckDlgButton(IDC_RAPPORT,1);

	GetDlgItem(IDC_VALEUR1)->SetFocus();
	
	return 0;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CDlgRapport::OnOK() 
{
	// TODO: Add extra validation here
	m_bRapport=IsDlgButtonChecked(IDC_RAPPORT);	
	m_bCompte=IsDlgButtonChecked(IDC_COUNT);
	m_bEtiquettes=IsDlgButtonChecked(IDC_ETIQUETTES);

	CDialog::OnOK();
}

void CDlgRapport::OnSelchangeListechamps1() 
{
	// TODO: Add your control notification handler code here
	GetDlgItem(IDC_VALEUR1)->SetFocus();
	
}

void CDlgRapport::OnSelchangeListechamps2() 
{
	// TODO: Add your control notification handler code here
	GetDlgItem(IDC_VALEUR2)->SetFocus();
	
}

void CDlgRapport::OnSelchangeListechamps3() 
{
	// TODO: Add your control notification handler code here
	GetDlgItem(IDC_VALEUR3)->SetFocus();
	
}
