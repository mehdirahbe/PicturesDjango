// DlgRenommerImage.cpp : implementation file
//

#include "stdafx.h"
#include "AccessDias.h"
#include "DlgRenommerImage.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CDlgRenommerImage dialog


CDlgRenommerImage::CDlgRenommerImage(CWnd* pParent /*=NULL*/)
	: CDialog(CDlgRenommerImage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CDlgRenommerImage)
	m_NouveauNom = _T("");
	//}}AFX_DATA_INIT
}


void CDlgRenommerImage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CDlgRenommerImage)
	DDX_Text(pDX, IDC_EDIT1, m_NouveauNom);
	DDV_MaxChars(pDX, m_NouveauNom, 100);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CDlgRenommerImage, CDialog)
	//{{AFX_MSG_MAP(CDlgRenommerImage)
		// NOTE: the ClassWizard will add message map macros here
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CDlgRenommerImage message handlers
