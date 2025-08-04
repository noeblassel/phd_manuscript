using LaTeXStrings,Plots


ε = 1e-2
lε = log(ε)

logspeedup(ln,lm) = log((10^ln-lε)/(exp(-lε/10^ln)*(10^ln/10^lm)-2lε))
pareff(ln,lm) = (10^ln-lε)/(exp(-lε/10^ln)*10^ln-2lε*10^lm)

lnrange = range(0,4,500)
lmrange = range(0,5,500)

fsize = 12

heatmap(lnrange,lmrange,logspeedup,xticks=(0:4,[L"10^{%$i}" for i=0:4]),yticks=(0:5,[L"10^{%$i}" for i=0:5]),xlabel=L"N^*",ylabel=L"N_{\mathrm{proc}}",title=L"\log_{10}\left(t^{\textbf{B1}-\textbf{E}}_{\mathrm{DNS}}/t^{\textbf{B1}-\textbf{E}}_{\mathrm{PR}}\right)\,(\varepsilon_{\mathrm{corr}}=0.01)",tickfontsize=fsize,labelfontsize=fsize,cmap=:viridis)
contour!(lnrange,lmrange,logspeedup,levels=0:6,linewidth=1,label="",color=:white)

savefig("logspeedup.pdf")

heatmap(lnrange,lmrange,pareff,xticks=(0:4,[L"10^{%$i}" for i=0:4]),yticks=(0:5,[L"10^{%$i}" for i=0:5]),xlabel=L"N^*",ylabel=L"N_{\mathrm{proc}}",title=L"t^{\textbf{B1}-\textbf{E}}_{\mathrm{DNS}}/\left(N_{\mathrm{proc}}t^{\textbf{B1}-\textbf{E}}_{\mathrm{PR}}\right)\,(\varepsilon_{\mathrm{corr}}=0.01)",tickfontsize=fsize,labelfontsize=fsize,cmap=:viridis)
contour!(lnrange,lmrange,pareff,levels=[0.5],linewidth=1,label="",color=:white)

savefig("parallel_efficiency.pdf")