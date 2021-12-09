py -u -W ignore run.py                         ^
  --train_file ..\data\websrc1.0_train_.json   ^
  --predict_file ..\data\websrc1.0_dev_.json   ^
  --root_dir ..\data --do_train                ^
  --model_type bert --method H-PLM             ^
  --model_name_or_path bert-base-uncased       ^
  --output_dir result\H-PLM_bert\              ^
  --do_lower_case --num_train_epochs 10 --no_cuda