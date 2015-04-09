import numpy # needed for various math tasks
import os # needed to arrange filenames alphabetically
import re # needed to arrange filenames alphabetically

def main():

    directory_path ='/Users/njoshi/Desktop/input_files'

    #detect all the .csv files in the folder
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    
    if (len(file_names) == 2):
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Cell events file: '+ file_names[0]
        print 'Reference variable file: '+ file_names[1]               
        calculateMutualInformation(file_names[0],file_names[1])
    else:
        print "Please make sure that there are an appropriate number of files in the folder"

#to make sure that the files are processed in the proper order
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def calculateMutualInformation (cell_events_file,reference_variable_file):

    raw_behavior = numpy.loadtxt(cell_events_file, dtype='int', comments='#', delimiter=',',skiprows=2)
    reference_variable = numpy.loadtxt(reference_variable_file, dtype='int', comments='#', delimiter=',',skiprows=2)

    total_number_of_frames = raw_behavior.shape[1]    
    total_number_of_cells = raw_behavior.shape[1]
    print 'Number of frames: %d'%total_number_of_frames
    print 'Number of cells: %d'%total_number_of_cells
    
    cell_mutual_information = numpy.zeros(total_number_of_cells,dtype='float')

    if (len(reference_variable) != total_number_of_frames):
        print 'Frame numbers do not match between events file and reference variable file'
        return
    else:
        print 'aaha!'

    #create an output folder for each input file
    output_dir_path = '/Users/njoshi/Desktop/output_files/'
    if output_dir_path:
        if not os.path.isdir(output_dir_path):
            os.makedirs(output_dir_path) 
    numpy.savetxt(output_dir_path + '/cell_events_per_frame.csv', cell_mutual_information , fmt='%i', delimiter=',', newline='\n')

################################################################################
#function MI = calcMI(cellEvents,externalTrace)

#get parameters
nCells=size(cellEvents,1);
nFrames=size(cellEvents,2);
MI = nan(nCells,1);

if (len(externalTrace) != nFrames):
    display('length of response and stimulus are not equal');
    return
else:
    #divide y to have nYvalues discrete values, range 0 to nYvalues-1
    #Y=round((stimulusSignal-min(stimulusSignal))*(nYvalues-1)/(max(stimulusSignal)-min(stimulusSignal)));
    Y=round(externalTrace-min(externalTrace));
    nYvalues=max(Y)+1;
end

# put X data into logical matrix
# zeros remain 0 and all other values (positive or negative) become 1
X=logical(cellEvents);

# calculate empirical probability distributions
logProbY=zeros(1,nYvalues);
logProbX0givenY=zeros(nCells, nYvalues);
logProbX1givenY=zeros(nCells, nYvalues);

for yVal in range(0,nYvalues-1):
    logProbY(yVal+1)=log(sum(Y==yVal))-log(nFrames);
    theseX=X(:,Y==yVal);
    logProbX0givenY(:,yVal+1)=log(sum(1-theseX,2)+1)-log(size(theseX,2)+2); #sum(1-theseX,2) means calculate sum of the array (1-theseX) in dimension#2,i.e. sum of each row
    logProbX1givenY(:, yVal+1)=log(sum(theseX,2)+1)-log(size(theseX,2)+2);
end
logProbX0=log(sum(1-X,2))-log(nFrames);
logProbX1=log(sum(X,2))-log(nFrames);
#B = repmat(A,n) returns an array containing n copies of A in the row and column dimensions. The size of B is size(A)*n when A is a matrix.
#B = repmat(A,r1,...,rN) specifies a list of scalars, r1,..,rN, that describes how copies of A are arranged in each dimension. When A has N dimensions, the size of B is size(A).*[r1...rN]. For example, repmat([1 2; 3 4],2,3) returns a 4-by-6 matrix.
logProbX0andY=log(exp(logProbX0givenY).*repmat(exp(logProbY),nCells,1));
logProbX1andY=log(exp(logProbX1givenY).*repmat(exp(logProbY),nCells,1));

% calculate MI
MI=sum(exp(logProbX0andY).*(logProbX0andY-repmat(logProbX0,1,nYvalues)-repmat(logProbY,nCells,1)),2)+...
    sum(exp(logProbX1andY).*(logProbX1andY-repmat(logProbX1,1,nYvalues)-repmat(logProbY,nCells,1)),2);
################################################################################   
    



###############################################################################
###############################################################################
###############################################################################    
    
#function MI = calcMI(cellEvents,externalTrace)
#
#% get parameters
#nCells=size(cellEvents,1);
#nFrames=size(cellEvents,2);
#MI = nan(nCells,1);
#
#if length(externalTrace)~=nFrames
#    display('length of response and stimulus are not equal');
#    return
#else
#    % divide y to have nYvalues discrete values, range 0 to nYvalues-1
#    %Y=round((stimulusSignal-min(stimulusSignal))*(nYvalues-1)/(max(stimulusSignal)-min(stimulusSignal)));
#    Y=round(externalTrace-min(externalTrace));
#    nYvalues=max(Y)+1;
#end
#% put X data into logical matrix
#X=logical(cellEvents);
#
#% calculate empirical probability distributions
#logProbY=zeros(1,nYvalues);
#logProbX0givenY=zeros(nCells, nYvalues);
#logProbX1givenY=zeros(nCells, nYvalues);
#for yVal=0:nYvalues-1
#    logProbY(yVal+1)=log(sum(Y==yVal))-log(nFrames);
#    theseX=X(:,Y==yVal);
#    logProbX0givenY(:,yVal+1)=log(sum(1-theseX,2)+1)-log(size(theseX,2)+2);
#    logProbX1givenY(:, yVal+1)=log(sum(theseX,2)+1)-log(size(theseX,2)+2);
#end
#logProbX0=log(sum(1-X,2))-log(nFrames);
#logProbX1=log(sum(X,2))-log(nFrames);
#logProbX0andY=log(exp(logProbX0givenY).*repmat(exp(logProbY),nCells,1));
#logProbX1andY=log(exp(logProbX1givenY).*repmat(exp(logProbY),nCells,1));
#
#% calculate MI
#MI=sum(exp(logProbX0andY).*(logProbX0andY-repmat(logProbX0,1,nYvalues)-repmat(logProbY,nCells,1)),2)+...
#    sum(exp(logProbX1andY).*(logProbX1andY-repmat(logProbX1,1,nYvalues)-repmat(logProbY,nCells,1)),2);