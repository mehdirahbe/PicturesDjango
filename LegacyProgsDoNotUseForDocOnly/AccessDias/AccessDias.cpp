// AccessDias.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "AccessDias.h"
#include "FicheDias.h"
#include "Accesdlg.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAccessDiasApp

const char * CAccessDiasApp::szChamps[]={"Sujet","Date","Boîte","Rangée","Numéro",
					"Sujet dias", "Agrandi","Classé","Vérifié","Commentaire",
					"Caméra digitale","Premier niveau","Second niveau",
					"Troisième niveau","Nom du fichier",
					//Uniquement pour tris (doit rester en dernier)
					"(Boîte+Rangée/Niveaux)+Numéro"};
int CAccessDiasApp::m_nNbreChampsTris=sizeof(CAccessDiasApp::szChamps)/sizeof(CAccessDiasApp::szChamps[0]);
int CAccessDiasApp::m_nNbreChampsRecherches=CAccessDiasApp::m_nNbreChampsTris-1;

BEGIN_MESSAGE_MAP(CAccessDiasApp, CWinApp)
	//{{AFX_MSG_MAP(CAccessDiasApp)
	//}}AFX_MSG_MAP
	ON_COMMAND(ID_HELP, CWinApp::OnHelp)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAccessDiasApp construction

CAccessDiasApp::CAccessDiasApp()
{
	// TODO: add construction code here,
	// Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CAccessDiasApp object

CAccessDiasApp theApp;

/////////////////////////////////////////////////////////////////////////////
// CAccessDiasApp initialization

BOOL CAccessDiasApp::InitInstance()
{
	// Standard initialization
	// If you are not using these features and wish to reduce the size
	//  of your final executable, you should remove from the following
	//  the specific initialization routines you do not need.

	LoadStdProfileSettings();  // Load standard INI file options (including MRU)

	CAccessDiasDlg dlg;
	m_pMainWnd = &dlg;
	int nResponse = dlg.DoModal();
	if (nResponse == IDOK)
	{
		// TODO: Place code here to handle when the dialog is
		//  dismissed with OK
	}
	else if (nResponse == IDCANCEL)
	{
		// TODO: Place code here to handle when the dialog is
		//  dismissed with Cancel
	}

	// Since the dialog has been closed, return FALSE so that we exit the
	//  application, rather than start the application's message pump.
	return FALSE;
}

