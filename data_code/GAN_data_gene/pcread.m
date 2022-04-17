%��ȡshapeNet�б�ǵĵ��ƣ����洢��.mat��
%03001627���� 04379243���� 02691156 �ɻ�  03790512 Ħ�г�
filelist=dir('H:\0retry_cv\shapenet_chair_pointcloud\03790512\points\*.pts');
seglist=dir('H:\0retry_cv\shapenet_chair_pointcloud\03790512\points_label\*.seg');
rootpath='H:\0retry_cv\shapenet_chair_pointcloud\03790512\points';
rootsegpath='H:\0retry_cv\shapenet_chair_pointcloud\03790512\points_label';

% %6778
% filelist=dir('H:\0retry_cv\shapenetcore_partanno_v0\PartAnnotation\03001627\points\*.pts');
% seglist=dir('H:\0retry_cv\shapenetcore_partanno_v0\PartAnnotation\03001627\points_label\*.seg');
% rootpath='H:\0retry_cv\shapenetcore_partanno_v0\PartAnnotation\03001627\points';

fileNum = length(filelist);

p2volume = zeros(fileNum,0,3);
for ii = 1:fileNum
    ii
    p2volumeeach=zeros(0,3);
    p2volumeeachseg=zeros(0,1);
    pts_filename = [rootpath filesep filelist(ii).name];
    seg_filename=[rootsegpath filesep seglist(ii).name];
    if strcmp(filelist(ii).name(1:end-4),seglist(ii).name(1:end-4))     
%     mesh = loadMesh(off_filename);
%     FV.vertices = mesh.V;
%     FV.faces = mesh.F;

        fid = fopen(pts_filename,'r');
        fidseg=fopen(seg_filename,'r');
        while ~feof(fid)
            line = strtrim(fgetl(fid));
            pointlist = strread(line,'%f');
            p2volumeeach(end+1,:)= pointlist;
        end
        while ~feof(fidseg)
            lineseg = strtrim(fgetl(fidseg));
            labellist = strread(lineseg,'%d');
            p2volumeeachseg(end+1)= labellist;
        end
        p2volume{ii}.name=filelist(ii).name;
        p2volume{ii}.ptc=p2volumeeach;
        p2volume{ii}.label=p2volumeeachseg;
        fclose(fid);
        fclose(fidseg);
    else
        disp('error');
        break;
    end
end    