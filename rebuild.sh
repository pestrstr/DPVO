cd DPViewer/
pip install .
cd ..
python demo.py  --imagedir ./movies/rgb_sequence \
                --calib=calib/d435.txt \
                --stride=1 --plot --viz \
                --config config/default.yaml \
                --save_reconstruction --save_trajectory 