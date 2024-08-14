// DlgUpdateComment.cpp : implementation file
//

#include "stdafx.h"
#include "AccessDias.h"
#include "DlgUpdateComment.h"


// CDlgUpdateComment dialog

IMPLEMENT_DYNAMIC(CDlgUpdateComment, CDialog)

CDlgUpdateComment::CDlgUpdateComment(CWnd* pParent /*=NULL*/)
	: CDialog(CDlgUpdateComment::IDD, pParent)
	, m_Comment(_T(""))
{

}

CDlgUpdateComment::~CDlgUpdateComment()
{
}

void CDlgUpdateComment::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	DDX_Text(pDX, IDC_NEWCOMMENT, m_Comment);
}


BEGIN_MESSAGE_MAP(CDlgUpdateComment, CDialog)
	ON_EN_CHANGE(IDC_NEWCOMMENT, &CDlgUpdateComment::OnEnChangeNewcomment)
END_MESSAGE_MAP()


// CDlgUpdateComment message handlers

void CDlgUpdateComment::OnEnChangeNewcomment()
{
	// TODO:  If this is a RICHEDIT control, the control will not
	// send this notification unless you override the CDialog::OnInitDialog()
	// function and call CRichEditCtrl().SetEventMask()
	// with the ENM_CHANGE flag ORed into the mask.

	// TODO:  Add your control notification handler code here
}
