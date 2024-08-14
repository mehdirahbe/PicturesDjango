// NewJpegSerie.cpp : implementation file
//

#include "stdafx.h"
#include "AccessDias.h"
#include "NewJpegSerie.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CNewJpegSerie dialog


CNewJpegSerie::CNewJpegSerie(CWnd* pParent /*=NULL*/)
	: CDialog(CNewJpegSerie::IDD, pParent)
{
	//{{AFX_DATA_INIT(CNewJpegSerie)
	m_Subject = _T("");
	m_Date = _T("");
	m_Commentaire = _T("");
	//}}AFX_DATA_INIT
}


void CNewJpegSerie::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CNewJpegSerie)
	DDX_Text(pDX, IDC_SUJET, m_Subject);
	DDX_Text(pDX, IDC_DATE, m_Date);
	DDX_Text(pDX, IDC_COMMENTAIRE, m_Commentaire);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CNewJpegSerie, CDialog)
	//{{AFX_MSG_MAP(CNewJpegSerie)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CNewJpegSerie message handlers

void CNewJpegSerie::OnOK() 
{
	// TODO: Add extra validation here
	
	CDialog::OnOK();
}
