// prephtml.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "lecture.h"
#include "memory"
#include "string"
#include "strsafe.h"

std::string g_szDirectory;

void ExportHTML(CFicheDias Dia,int nNoImg,BOOL bBig,int nCountHTML)
{
	char szName[256];
	FILE *hf;
	char l_szJpegName[sizeof(Dia.m_NomFichier)];
	
	if (*Dia.m_NomFichier)
		StringCchCopy(l_szJpegName,sizeof(l_szJpegName),Dia.m_NomFichier);
	else
		sprintf_s(l_szJpegName,sizeof(l_szJpegName),"%03d.jpg",nNoImg);
	
	if (bBig)
		sprintf_s(szName,sizeof(szName),"%sbig-html/%03d.html",g_szDirectory.c_str(),nNoImg);
	else
		sprintf_s(szName,sizeof(szName),"%sview-html/%03d.html",g_szDirectory.c_str(),nNoImg);
	fopen_s(&hf,szName,"wt");
	fprintf(hf,"<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	fprintf(hf,"<title>%s</title></head><body>\n",Dia.m_SujetDias);
	
	if (nNoImg<nCountHTML-1)
	{
		if (bBig)
			fprintf(hf,"<a href=\"%03d.html\"><img SRC=\"../big/%s\" alt=\"%s\"></a><br>&nbsp;\n",nNoImg+1,l_szJpegName,Dia.m_SujetDias);
		else
			fprintf(hf,"<a href=\"%03d.html\"><img SRC=\"../view/%s\" alt=\"%s\"></a><br>&nbsp;\n",nNoImg+1,l_szJpegName,Dia.m_SujetDias);
	}
	else
	{
		if (bBig)
			fprintf(hf,"<img SRC=\"../big/%s\" alt=\"%s\"><br>&nbsp;\n",l_szJpegName,Dia.m_SujetDias);
		else
			fprintf(hf,"<img SRC=\"../view/%s\" alt=\"%s\"><br>&nbsp;\n",l_szJpegName,Dia.m_SujetDias);
	}
	fprintf(hf,"<dd>%s</dd><br>&nbsp;\n",Dia.m_SujetDias);  
	if (strlen(Dia.m_Commentaire))
		fprintf(hf,"<dd>%s</dd><br>&nbsp;\n",Dia.m_Commentaire);  
	
	if (!Dia.m_bCameraDigitale)
		fprintf(hf,"<p><br>R&eacute;f&eacute;rence de la dias: %s, %u, n° %u (pris le %s)\n",
		Dia.m_Boite,Dia.m_nRangee,Dia.m_nNumero,Dia.m_Date);
	else
	{
		if (*Dia.m_TroisiemeNiveau)
			fprintf(hf,"<p><br>R&eacute;f&eacute;rence du fichier raw: %s/%s/%s/%s, n° %u (pris le %s)\n",
			Dia.m_PremierNiveau,Dia.m_SecondNiveau,Dia.m_TroisiemeNiveau,l_szJpegName,Dia.m_nNumero,Dia.m_Date);
		else
			fprintf(hf,"<p><br>R&eacute;f&eacute;rence du fichier raw: %s/%s/%s, n° %u (pris le %s)\n",
			Dia.m_PremierNiveau,Dia.m_SecondNiveau,l_szJpegName,Dia.m_nNumero,Dia.m_Date);
	}
	
	if (nNoImg>1)
		fprintf(hf,"<p><a href=\"%03d.html\">Dia pr&eacute;c&eacute;dente</a>\n",nNoImg-1);
	if (nNoImg<nCountHTML-1)
		fprintf(hf,"<br><a href=\"%03d.html\">Dia suivante</a>\n",nNoImg+1);
	if (!bBig)
	{
		fprintf(hf,"<br><a href=\"../big-html/%03d.html\">Grande version</a>\n",nNoImg);
		fprintf(hf,"<br><a href=\"../planchecontact.html\">Retour &agrave; la planche contact</a>\n");
	}
	else
	{
		fprintf(hf,"<br><a href=\"../view-html/%03d.html\">Petite version</a>\n",nNoImg);
		fprintf(hf,"<br><a href=\"../planchecontact-big.html\">Retour &agrave; la planche contact</a>\n");
	}
	fprintf(hf,"</body></html>\n");
	fclose(hf);
}

int TreatFile(char *l_pDiasDB, const char *pszSubject,int p_nCountHTML, BOOL p_bComputeCountOnly,bool p_bCreateBigHTML)
{
	char *pCurView=l_pDiasDB;
	UINT nNoImg=1;
	
	UINT nVersion;
	
	FILE *l_hContactSheet=NULL;
	if (!p_bComputeCountOnly)
	{
		if (p_bCreateBigHTML)
			fopen_s(&l_hContactSheet,(g_szDirectory+"planchecontact-big.html").c_str(),"wt");
		else
			fopen_s(&l_hContactSheet,(g_szDirectory+"planchecontact.html").c_str(),"wt");
		if (!l_hContactSheet)
		{
			printf("Impossible d'ouvrir la planche contact\n");
			return -1;
		}
		fprintf(l_hContactSheet,"<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	}
	
	nVersion=*((UINT *)pCurView);
	pCurView+=sizeof(UINT);
	if (nVersion>=100) {
		UINT nFiches,nCompt;
		
		nFiches=*((UINT *)pCurView);
		pCurView+=sizeof(UINT);
		
		for (nCompt=0;nCompt<nFiches;nCompt++) {
			CFicheDias Dia;
			
			StringCchCopy(Dia.m_Sujet,sizeof(Dia.m_Sujet),pCurView);
			pCurView+=strlen(Dia.m_Sujet)+1;
			
			StringCchCopy(Dia.m_Date,sizeof(Dia.m_Date),pCurView);
			pCurView+=strlen(Dia.m_Date)+1;
			
			StringCchCopy(Dia.m_Boite,sizeof(Dia.m_Boite),pCurView);
			pCurView+=strlen(Dia.m_Boite)+1;
			
			Dia.m_nRangee=*((UINT *)pCurView);
			pCurView+=sizeof(UINT);
			
			Dia.m_nNumero=*((UINT *)pCurView);
			
			pCurView+=sizeof(UINT);
			
			StringCchCopy(Dia.m_SujetDias,sizeof(Dia.m_SujetDias),pCurView);
			pCurView+=strlen(Dia.m_SujetDias)+1;
			
			Dia.m_bAgrandi=*((BOOL *)pCurView);
			pCurView+=sizeof(BOOL);
			
			Dia.m_bClasse=*((BOOL *)pCurView);
			pCurView+=sizeof(BOOL);
			
			Dia.m_bVerifie=*((BOOL *)pCurView);
			pCurView+=sizeof(BOOL);
			
			StringCchCopy(Dia.m_Commentaire,sizeof(Dia.m_Commentaire),pCurView);
			pCurView+=strlen(Dia.m_Commentaire)+1;
			
			if (nVersion>=101) {
				Dia.m_bCameraDigitale=*((BOOL *)pCurView);
				pCurView+=sizeof(BOOL);
				
				StringCchCopy(Dia.m_PremierNiveau,sizeof(Dia.m_PremierNiveau),pCurView);
				pCurView+=strlen(Dia.m_PremierNiveau)+1;
				
				StringCchCopy(Dia.m_SecondNiveau,sizeof(Dia.m_SecondNiveau),pCurView);
				pCurView+=strlen(Dia.m_SecondNiveau)+1;
				
				if (nVersion>=102) {
					StringCchCopy(Dia.m_TroisiemeNiveau,sizeof(Dia.m_TroisiemeNiveau),pCurView);
					pCurView+=strlen(Dia.m_TroisiemeNiveau)+1;
					
					if (nVersion>=103) {
						StringCchCopy(Dia.m_NomFichier,sizeof(Dia.m_NomFichier),pCurView);
						pCurView+=strlen(Dia.m_NomFichier)+1;
					}
				}
			}
			
			if (Dia.m_bAgrandi) {
				if (!_stricmp(Dia.m_Sujet,pszSubject)) {
					if (!p_bComputeCountOnly) {
						
						if (nNoImg==1)
						{
							fprintf(l_hContactSheet,"<title>%s</title></head><body><center>\n",Dia.m_Sujet);
							fprintf(l_hContactSheet,"<table BORDER COLS=4 WIDTH=\"100%\" NOSAVE >\n<tr>\n");
						}
						
						if ((nNoImg-1) && ((nNoImg-1)%4)==0)
						{
							fprintf(l_hContactSheet,"</tr>\n");
							fprintf(l_hContactSheet,"<tr>\n");
						}
						
						char l_szJpegName[sizeof(Dia.m_NomFichier)];
						
						if (*Dia.m_NomFichier)
							StringCchCopy(l_szJpegName,sizeof(l_szJpegName),Dia.m_NomFichier);
						else
							sprintf_s(l_szJpegName,sizeof(l_szJpegName),"%03d.jpg",nNoImg);
						
						fprintf(l_hContactSheet,"<td><a href=\"%s-html/%03d.html\"><img SRC=\"contactsheet/%s\" alt=\"%s\"></a></td>\n",
							(p_bCreateBigHTML) ? "big":"view",nNoImg,l_szJpegName,Dia.m_SujetDias);
						
						
						if (p_bCreateBigHTML)
							ExportHTML(Dia,nNoImg,true,p_nCountHTML);
						else
							ExportHTML(Dia,nNoImg,false,p_nCountHTML);
					}
					nNoImg++;
				}
			}
		}
	}
	
	if (l_hContactSheet)
	{
		if (p_bCreateBigHTML)
			fprintf(l_hContactSheet,"</tr>\n</table></center><a href=\"planchecontact.html\">Petites images</a>");
		else
			fprintf(l_hContactSheet,"</tr>\n</table></center><a href=\"planchecontact-big.html\">Grandes images</a>");
		fprintf(l_hContactSheet,"<br><a href=\"../index.html\">Retour</a>\n");
		fprintf(l_hContactSheet,"</body></html>");
		fclose(l_hContactSheet);
	}
	
	return nNoImg;
}

int main(int argc,char **argv,char **envp)
{
	FILE *l_hfDiasDB;
	struct stat Stat;
	
	BOOL l_bComputeCountOnly=false;
	
	if (argc<4) {
		printf("Il faut préciser le chemin du batch appelant, le nom de la base et le sujet\n");
		printf("Si -f est mis, indique uniquement les références des dias.\n");
		return(0);
	}
	
	if (strcmp(argv[1],"-f")==0) {
		l_bComputeCountOnly=true;
		argc--;
		argv++;
	}
	const char *l_pszBatch=argv[1];
	const char *l_pszBase=argv[2];
	const char *l_pszSujet=argv[3];
	
	//Change le répertoire courant afin de se mettre ou est le batch
	char l_szBatch[256];
	StringCchCopy(l_szBatch,sizeof(l_szBatch),l_pszBatch);
	char *l_pszLastSlash=strrchr(l_szBatch,'\\');
	if (l_pszLastSlash)
	{
		l_pszLastSlash[1]=0;
		g_szDirectory=l_szBatch;
	}
	printf("Le répertoire de base est: %s\n",g_szDirectory.c_str());
	
	fopen_s(&l_hfDiasDB,l_pszBase,"rb");
	if(!l_hfDiasDB)
	{
		printf("Impossible d'ouvrir le fichier %s\n",l_pszBase);
		return(0);
	}
	
	if (!l_bComputeCountOnly)
	{
		CreateDirectory((g_szDirectory+"big-html").c_str(),NULL);
		CreateDirectory((g_szDirectory+"view-html").c_str(),NULL);
	}
	
	fstat(_fileno(l_hfDiasDB), &Stat);
	
	std::auto_ptr<char> l_pDiasDB(new char[Stat.st_size]);
	fread(l_pDiasDB.get(),Stat.st_size,1,l_hfDiasDB);
	fclose(l_hfDiasDB);
	
	char l_szSubject[512];
	CharToOem(l_pszSujet,l_szSubject);
	
	if (Stat.st_size) {
		//Compute count
		int l_nCountHTML=TreatFile(l_pDiasDB.get(), l_szSubject, -1, true,false);
		
		if (!l_bComputeCountOnly && l_nCountHTML>0)
		{
			//Create big
			TreatFile(l_pDiasDB.get(), l_szSubject, l_nCountHTML, false,true);
			//Create small
			TreatFile(l_pDiasDB.get(), l_szSubject, l_nCountHTML, false,false);
		}
	}
	return(0);
}

