#! /bin/bash
set -e
set -u
################################################################################
DIR_OUT="../data_in"
################################################################################
if [ ! -d "${DIR_OUT}" ]; then
  mkdir "${DIR_OUT}"
fi

if [ ! -d "${DIR_OUT}/broadcast" ]; then
  mkdir "${DIR_OUT}/broadcast"
fi
rm -vf "${DIR_OUT}/broadcast/baserad.zip"
curl "http://www.ic.gc.ca/engineering/BC_DBF_FILES/baserad.zip" -o "${DIR_OUT}/broadcast/baserad.zip"
rm -vf "${DIR_OUT}/broadcast/Broadcast_Database_Extract_Manual.pdf"
curl "http://sms-sgs.ic.gc.ca/eic/site/sms-sgs-prod.nsf/vwapj/Broadcast_Database_Extract_Manual.pdf/\$file/Broadcast_Database_Extract_Manual.pdf" -o "${DIR_OUT}/broadcast/Broadcast_Database_Extract_Manual.pdf"
unzip -o "${DIR_OUT}/broadcast/baserad.zip" -d "${DIR_OUT}/broadcast"
mv "${DIR_OUT}/broadcast/baserad/"*dbf "${DIR_OUT}/broadcast/"
mv "${DIR_OUT}/broadcast/baserad/"*DBF "${DIR_OUT}/broadcast/"

if [ ! -d "${DIR_OUT}/spectrum_site" ]; then
  mkdir "${DIR_OUT}/spectrum_site"
fi
rm -vf "${DIR_OUT}/spectrum_site/Site_Data_Extract.zip"
curl "http://www.ic.gc.ca/engineering/SMS_TAFL_Files/Site_Data_Extract.zip" -o "${DIR_OUT}/spectrum_site/Site_Data_Extract.zip"
rm -vf "${DIR_OUT}/spectrum_site/readme_site_data.pdf"
curl "http://www.ic.gc.ca/engineering/SMS_TAFL_Files/readme_site_data.pdf" -o "${DIR_OUT}/spectrum_site/readme_site_data.pdf"
unzip -o "${DIR_OUT}/spectrum_site/Site_Data_Extract.zip" -d "${DIR_OUT}/spectrum_site"

if [ ! -d "${DIR_OUT}/spectrum_auth" ]; then
  mkdir "${DIR_OUT}/spectrum_auth"
fi
rm -vf "${DIR_OUT}/spectrum_auth/TAFL_LTAF.zip"
curl "http://www.ic.gc.ca/engineering/SMS_TAFL_Files/TAFL_LTAF.zip" -o "${DIR_OUT}/spectrum_auth/TAFL_LTAF.zip"
rm -vf "${DIR_OUT}/spectrum_auth/tafl_description_ltaf.pdf"
curl "http://sms-sgs.ic.gc.ca/eic/site/sms-sgs-prod.nsf/vwapj/tafl_description_ltaf.pdf/\$file/tafl_description_ltaf.pdf" -o "${DIR_OUT}/spectrum_auth/tafl_description_ltaf.pdf"
unzip -o "${DIR_OUT}/spectrum_auth/TAFL_LTAF.zip" -d "${DIR_OUT}/spectrum_auth"
