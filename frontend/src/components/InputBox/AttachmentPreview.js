import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const PreviewContainer = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
`;

const PreviewItem = styled.div`
  position: relative;
  width: 80px;
  height: 60px;
  border-radius: 12px;
  overflow: hidden;
  background: ${({ theme }) => theme.colors.attachmentBg};
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
`;

const PreviewImage = styled.img`
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
`;

const RemoveButton = styled.button`
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(255,255,255,0.8);
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  color: #333;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  user-select: none;

  &:hover,
  &:focus {
    background: rgba(255,255,255,1);
    outline: none;
  }
`;

const FileIcon = styled.div`
  font-size: 24px;
  color: ${({ theme }) => theme.colors.textSecondary};
`;

function AttachmentPreview({ attachments, onRemove }) {
  if (!attachments || attachments.length === 0) return null;

  return (
    <PreviewContainer aria-label="Attachment previews" role="list">
      {attachments.map((att, idx) => {
        const isImage = att.type && att.type.startsWith('image');
        return (
          <PreviewItem key={att.id || att.name || idx} role="listitem">
            {isImage && att.url ? (
              <PreviewImage src={att.url} alt={att.filename || 'attachment'} />
            ) : (
              <FileIcon aria-label="File attachment">📄</FileIcon>
            )}
            <RemoveButton
              type="button"
              aria-label={`Remove attachment ${att.filename || 'file'}`}
              onClick={() => onRemove(idx)}
            >
              ×
            </RemoveButton>
          </PreviewItem>
        );
      })}
    </PreviewContainer>
  );
}

AttachmentPreview.propTypes = {
  attachments: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      url: PropTypes.string.isRequired,
      filename: PropTypes.string,
      type: PropTypes.string,
      name: PropTypes.string,
    })
  ),
  onRemove: PropTypes.func.isRequired,
};

export default AttachmentPreview;
