export interface DocumentItem {
  srID: string;
  serviceID: number;
  code: string;
  title: string;
  description: string;
  requirementType: 'REQUIRED' | 'OPTIONAL' | 'OCR_REQUIREMENT' | 'CONDITIONAL' | 'OCR_REQUIRED_CONDITIONAL';
  ocr_enabled: boolean;
  connect: string[];
  color: string | null;
  files: string[] | null;
}

export interface ScanFile {
  url: string;
  link: string;
}

export interface SendFile {
  srID: string;
  files: string[];
}
