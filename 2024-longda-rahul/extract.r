library(Seurat)
library(io)
library(dplyr)

argv <- commandArgs(trailingOnly=TRUE)

if (length(argv) == 0) {
	stop("usage: script <file>")
}

#in.fn <- "Seurat_object_IFNB_Perturb_seq.rds";

in.fn <- argv[1];

gene <- "TERT";
experiment <- tolower(strsplit(in.fn, "_")[[1]][3]);

out.fn <- filename("nadig24", tag=c(experiment, "obs", tolower(gene)), ext="rds", date=NA);

x <- qread(in.fn);

cdata <- x[[c("cell_type", "sample_ID", "gene", "Batch_info", "nCount_RNA", "percent.mito")]];

table(cdata$cell_type)
table(cdata$cell_type, cdata$sample_ID);

gene <- "TERT";
cdata$tert <- x[["RNA"]]$counts[gene, ];

out <- select(cdata, cell_type, target_gene=gene, batch=sample_ID, batch2=Batch_info, total_counts=nCount_RNA, pct_mito=percent.mito, tert);
rownames(out) <- NULL;
out$batch <- sub("sample_", "", out$batch);
out$batch2 <- sub("Rep", "", out$batch2);
out$batch <- factor(out$batch);
out$batch2 <- factor(out$batch2);
out$target_gene <- factor(out$target_gene);
out$cell_type <- factor(out$cell_type);

ct <- table(out$tert);
prop.table(ct)

mean(out$pct_mito > 10)

qwrite(out, out.fn);

