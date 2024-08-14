#include "stdafx.h"
#include "FicheDias.h"

int CBanqueDias::LitBanque(LPCTSTR pszNomFich)
{
CWaitCursor DoWait;
HANDLE hFile=CreateFile(pszNomFich,GENERIC_READ,FILE_SHARE_READ,
    						0,OPEN_EXISTING,FILE_FLAG_SEQUENTIAL_SCAN,0);	

	m_Dias.RemoveAll();

	if (!hFile)
		return(0);

	HANDLE hMap=CreateFileMapping(hFile,0,PAGE_READONLY,0,0,NULL);
	char *pView=(char *)MapViewOfFile(hMap,FILE_MAP_READ,0,0,0);
	char *pCurView=pView;
	if (pView) {
		UINT nVersion;

		nVersion=*((UINT *)pCurView);
		pCurView+=sizeof(UINT);
		if (nVersion>=100) {
			try {
				UINT nFiches,nCompt;

				nFiches=*((UINT *)pCurView);
				pCurView+=sizeof(UINT);
				m_Dias.SetSize(nFiches);

				for (nCompt=0;nCompt<nFiches;nCompt++) {
					CFicheDias &Dia=m_Dias[nCompt];

					Dia.m_Sujet=pCurView;
					pCurView+=Dia.m_Sujet.GetLength()+1;

					Dia.m_Date=pCurView;
					pCurView+=Dia.m_Date.GetLength()+1;

					Dia.m_Boite=pCurView;
					pCurView+=Dia.m_Boite.GetLength()+1;

					Dia.m_nRangee=*((UINT *)pCurView);
					pCurView+=sizeof(UINT);
				
					Dia.m_nNumero=*((UINT *)pCurView);
					pCurView+=sizeof(UINT);

					Dia.m_SujetDias=pCurView;
					pCurView+=Dia.m_SujetDias.GetLength()+1;

					Dia.m_bAgrandi=*((BOOL *)pCurView);
					pCurView+=sizeof(BOOL);

					Dia.m_bClasse=*((BOOL *)pCurView);
					pCurView+=sizeof(BOOL);
				
					Dia.m_bVerifie=*((BOOL *)pCurView);
					pCurView+=sizeof(BOOL);

					Dia.m_Commentaire=pCurView;
					pCurView+=Dia.m_Commentaire.GetLength()+1;

					if (nVersion>=101)
					{
						Dia.m_bCameraDigitale=*((BOOL *)pCurView);
						pCurView+=sizeof(BOOL);

						Dia.m_PremierNiveau=pCurView;
						pCurView+=Dia.m_PremierNiveau.GetLength()+1;

						Dia.m_SecondNiveau=pCurView;
						pCurView+=Dia.m_SecondNiveau.GetLength()+1;
						
						if (nVersion>=102)
						{
							Dia.m_TroisiemeNiveau=pCurView;
							pCurView+=Dia.m_TroisiemeNiveau.GetLength()+1;
							if (nVersion>=103)
							{
								Dia.m_NomFichierJpeg=pCurView;
								//In case where conversion is forced, done 1 shot in 2017
								//Dia.m_NomFichierJpeg.MakeLower();
								pCurView+=Dia.m_NomFichierJpeg.GetLength()+1;
							}
						}

					}
				}
			}
			catch (CMemoryException me) {
				m_Dias.RemoveAll();
			}
		}
		CloseHandle(hMap);
		UnmapViewOfFile(pView);
	}
	CloseHandle(hFile);
	return(m_Dias.GetSize());
}

int CBanqueDias::SauveBanque(LPCTSTR pszNomFich)
{
FILE *hFile=NULL;
//La version (à incrémenter quand la structure change)
UINT nVal=103,nCompt;
CWaitCursor DoWait;

	if (!m_Dias.GetSize())
		return(0);

	fopen_s(&hFile,pszNomFich,"wb");
	if (!hFile)
		return(0);

	/*Sauve version et taille*/
	fwrite(&nVal,sizeof(UINT),1,hFile);
	nVal=m_Dias.GetSize();
	fwrite(&nVal,sizeof(UINT),1,hFile);

	for (nCompt=0;nCompt<(UINT)m_Dias.GetSize();nCompt++) {
		CFicheDias &Dia=m_Dias[nCompt];

		fwrite((LPCTSTR)Dia.m_Sujet,Dia.m_Sujet.GetLength()+1,1,hFile);
		fwrite((LPCTSTR)Dia.m_Date,Dia.m_Date.GetLength()+1,1,hFile);
		fwrite((LPCTSTR)Dia.m_Boite,Dia.m_Boite.GetLength()+1,1,hFile);
		fwrite(&Dia.m_nRangee,sizeof(UINT),1,hFile);
		fwrite(&Dia.m_nNumero,sizeof(UINT),1,hFile);
		fwrite((LPCTSTR)Dia.m_SujetDias,Dia.m_SujetDias.GetLength()+1,1,hFile);
		fwrite(&Dia.m_bAgrandi,sizeof(BOOL),1,hFile);
		fwrite(&Dia.m_bClasse,sizeof(BOOL),1,hFile);
		fwrite(&Dia.m_bVerifie,sizeof(BOOL),1,hFile);
		fwrite((LPCTSTR)Dia.m_Commentaire,Dia.m_Commentaire.GetLength()+1,1,hFile);
		fwrite(&Dia.m_bCameraDigitale,sizeof(BOOL),1,hFile);
		fwrite((LPCTSTR)Dia.m_PremierNiveau,Dia.m_PremierNiveau.GetLength()+1,1,hFile);
		fwrite((LPCTSTR)Dia.m_SecondNiveau,Dia.m_SecondNiveau.GetLength()+1,1,hFile);
		fwrite((LPCTSTR)Dia.m_TroisiemeNiveau,Dia.m_TroisiemeNiveau.GetLength()+1,1,hFile);
		fwrite((LPCTSTR)Dia.m_NomFichierJpeg,Dia.m_NomFichierJpeg.GetLength()+1,1,hFile);
	}

	fclose(hFile);
	return(1);
}


int CBanqueDias::CreeFiche(int bTakeLast)
{
	try {
		int nMax=m_Dias.GetSize();

		m_Dias.SetSize(nMax+1);

		if (nMax && bTakeLast) {
			CFicheDias &DiaLast=m_Dias[nMax-1];
			CFicheDias &DiaNouv=m_Dias[nMax];

			DiaNouv=DiaLast;

			DiaNouv.m_nNumero++;

			//Si c'est réellement une dias
			if (!DiaNouv.m_bCameraDigitale)
			{
				//Nouvelle rangée dans la boîte
				if (DiaNouv.m_nNumero>50)
				{
					DiaNouv.m_nNumero=1;
					DiaNouv.m_nRangee++;
				}
			}
		}
	}
	catch (CMemoryException me) {
		m_Dias.RemoveAll();
	}
	return(m_Dias.GetSize());
}

int CBanqueDias::InsereFiche(int nIndex,int bTakeLast)
{
	try {
		CFicheDias Dia;

		if (bTakeLast)
			Dia=m_Dias[nIndex];
		m_Dias.InsertAt(nIndex, Dia);
	}
	catch (CMemoryException me) {
		return(0);
	}
	return(1);
}

//Remove all space from a box number
char *RemoveSpaces(const char *pszBoxNumberString,char *pszDest,size_t p_nDestSize);

int CBanqueDias::CorrespondsCritere(int nNoFiche,CString *pValChamp,int nChamp[3])
{
	CFicheDias &Dia=m_Dias[nNoFiche];
	int bOK=1,nCompt;
	CString Tmp;

	/*Les critères*/
	for (nCompt=0;nCompt<3;nCompt++) {
		/*Actif ?*/
		if (pValChamp[nCompt].GetLength()) {
			switch (nChamp[nCompt]) {
				case 0:	/*Sujet*/
					Tmp=Dia.m_Sujet;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
				case 1:	/*Date*/
					Tmp=Dia.m_Date;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
				case 2:	/*Boîte*/
					{
						char szCleanedRec[20],szCleanedToFind[20];

						RemoveSpaces(Dia.m_Boite,szCleanedRec,sizeof(szCleanedRec));
						RemoveSpaces(pValChamp[nCompt],szCleanedToFind,sizeof(szCleanedToFind));

						Tmp=szCleanedRec;
						Tmp.MakeUpper();
						if (Tmp.Find(szCleanedToFind)==-1)
							bOK=0;
						break;
					}
				case 3:	/*Rangée*/
					if (Dia.m_nRangee!=(UINT)atoi(pValChamp[nCompt]))
						bOK=0;
					break;
				case 4:	/*Numéro*/
					if (Dia.m_nNumero!=(UINT)atoi(pValChamp[nCompt]))
						bOK=0;
					break;
				case 5:	/*Sujet dias*/
					Tmp=Dia.m_SujetDias;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
				case 6:	/*Agrandi*/
					if (!Dia.m_bAgrandi && !pValChamp[nCompt].CompareNoCase("V"))
						bOK=0;
					break;
				case 7:	/*Classé*/
					if (!Dia.m_bClasse && !pValChamp[nCompt].CompareNoCase("V"))
						bOK=0;
					break;
				case 8:	/*Vérifié*/
					if (!Dia.m_bVerifie && !pValChamp[nCompt].CompareNoCase("V"))
						bOK=0;
					break;
				case 9:	/*Commentaire*/
					Tmp=Dia.m_Commentaire;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
				case 10:	/*Caméra Digitale*/
					if (!Dia.m_bCameraDigitale && !pValChamp[nCompt].CompareNoCase("V"))
						bOK=0;
					break;
				case 11:	/*Premier niveau*/
					Tmp=Dia.m_PremierNiveau;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
				case 12:	/*Second niveau*/
					Tmp=Dia.m_SecondNiveau;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
				case 13:	/*Troisième niveau*/
					Tmp=Dia.m_TroisiemeNiveau;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
				case 14:	/*Nom du fichier*/
					Tmp=Dia.m_NomFichierJpeg;
					Tmp.MakeUpper();
					if (Tmp.Find(pValChamp[nCompt])==-1)
						bOK=0;
					break;
			}
			if (!bOK)
				break;
		}
	}

	return(bOK);
}
