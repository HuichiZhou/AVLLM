export CUDA_VISIBLE_DEVICES=1
   for name in textfooler
   do
    textattack attack --recipe $name --model bert-base-uncased-mr --dataset-from-huggingface mr --dataset-split test --constraints tinyllama --num-examples 1000 --shuffle --log-to-txt ${name}-bert-mr.txt --log-to-csv ${name}-bert-mr.csv
   done