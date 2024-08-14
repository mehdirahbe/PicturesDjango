#pragma once


// CDlgUpdateComment dialog

class CDlgUpdateComment : public CDialog
{
	DECLARE_DYNAMIC(CDlgUpdateComment)

public:
	CDlgUpdateComment(CWnd* pParent = NULL);   // standard constructor
	virtual ~CDlgUpdateComment();

// Dialog Data
	enum { IDD = IDD_DLG_UPDATECOMMENT };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnEnChangeNewcomment();
public:
	CString m_Comment;
};
